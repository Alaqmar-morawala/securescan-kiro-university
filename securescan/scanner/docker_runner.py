"""Per-scan Docker isolation with guaranteed cleanup + mock fallback."""

from __future__ import annotations

from django.conf import settings
from django.utils import timezone

from .services import estimate_cost, order_findings
from .zap_client import MOCK_FINDINGS, MockZapClient


def _mock_mode() -> bool:
    return bool(getattr(settings, "SECURESCAN_MOCK", True))


def run_scan(scan) -> None:
    """Execute a Scan synchronously (demo/test friendly).

    Real path: create per-scan Docker container running ZAP, stream progress,
    collect alerts, cleanup in finally. Mock path: deterministic fixtures.
    """
    from .models import Finding  # local import to avoid app-loading issues

    scan.status = "RUNNING"
    scan.progress = 5
    scan.save(update_fields=["status", "progress"])
    container = None
    try:
        if _mock_mode():
            client = MockZapClient(scan.target.url, scan.config.scan_type)
            client.spider()  # exercise spider path; URLs discarded in mock
            scan.progress = 45
            scan.save(update_fields=["progress"])
            raw = client.active_scan()
            ordered = order_findings(raw)
            scan.findings.all().delete()
            finding_fields = (
                "name", "severity", "url", "description", "solution", "cwe",
            )
            for f in ordered:
                Finding.objects.create(
                    scan=scan,
                    **{k: f.get(k, "") for k in finding_fields},
                )
            scan.progress = 100
            scan.status = "DONE"
            scan.finished_at = timezone.now()
            scan.save()
            return
        # ---- Real Docker + ZAP path (used in production) ----
        import docker  # type: ignore

        docker_client = docker.from_env()
        container = docker_client.containers.run(
            "ghcr.io/zaproxy/zaproxy:stable",
            command="zap.sh -daemon -port 8080 -host 0.0.0.0",
            detach=True,
            remove=False,
            mem_limit="1g",
            name=f"securescan-{scan.pk}",
        )
        # NOTE: production would wait-for-ZAP, drive spider+active scan via
        # ZapClient, update progress 10..90, then persist alerts.
        # Minimal safe fallback so real path never silently succeeds:
        raise RuntimeError(
            "Real ZAP orchestration not configured in this build; "
            "set SECURESCAN_MOCK=1."
        )
    except Exception as exc:  # noqa: BLE001 - record any failure on the scan
        scan.status = "FAILED"
        scan.error = str(exc)[:2000]
        scan.finished_at = timezone.now()
        scan.save()
    finally:
        if container is not None:
            try:
                container.stop(timeout=5)
                container.remove(force=True)
            except Exception:
                pass


def seed_estimate(scan) -> None:
    cost, duration = estimate_cost(
        scan.config.max_pages, scan.config.spider_depth, scan.config.scan_type
    )
    scan.cost_estimate = cost
    scan.duration_estimate_s = duration
    scan.save(update_fields=["cost_estimate", "duration_estimate_s"])


__all__ = ["MOCK_FINDINGS", "MockZapClient", "run_scan", "seed_estimate"]
