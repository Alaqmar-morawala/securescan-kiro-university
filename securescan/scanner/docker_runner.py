"""Scan execution: mock fixtures or the real ZAP engine (local or Docker).

Engine selection lives in :mod:`scanner.engine`. The real path enforces the
SSRF target guard (``scanner.guards``) before any fetch happens, then drives
ZAP either through a local/reused daemon (``SECURESCAN_ZAP_LAUNCHER=local``,
default) or a per-scan Docker container (``=docker``, guaranteed cleanup in
``finally``).
"""

from __future__ import annotations

import logging
import time

from django.conf import settings
from django.utils import timezone

from .engine import build_client, resolve_engine
from .guards import validate_scan_target
from .services import estimate_cost, order_findings
from .zap_client import MOCK_FINDINGS, MockZapClient, RealZapClient

logger = logging.getLogger(__name__)

FINDING_FIELDS = ("name", "severity", "url", "description", "solution", "cwe")
ZAP_IMAGE = "ghcr.io/zaproxy/zaproxy:stable"


def run_scan(scan, *, engine=None) -> None:
    """Execute a Scan to completion (recording status on the row).

    ``engine`` is injectable for tests; by default resolved from settings
    via :func:`scanner.engine.resolve_engine`.
    """
    scan.status = "RUNNING"
    scan.progress = 5
    scan.save(update_fields=["status", "progress"])
    container_box: list = []
    try:
        plan = engine or resolve_engine()
        if not plan.is_real:
            _run_mock(scan)
        elif getattr(settings, "SECURESCAN_ZAP_LAUNCHER", "local") == "docker":
            _run_real_docker(scan, container_box)
        else:
            _run_real_local(scan)
    except Exception as exc:  # noqa: BLE001 - record any failure on the scan
        scan.status = "FAILED"
        scan.error = str(exc)[:2000]
        scan.finished_at = timezone.now()
        scan.save()
    finally:
        for container in container_box:
            try:
                container.stop(timeout=5)
                container.remove(force=True)
            except Exception:
                pass


def _finish(scan) -> None:
    scan.progress = 100
    scan.status = "DONE"
    scan.finished_at = timezone.now()
    scan.save()


def _persist_findings(scan, raw: list[dict]) -> None:
    from .models import Finding  # local import to avoid app-loading issues

    ordered = order_findings(raw)
    scan.findings.all().delete()
    Finding.objects.bulk_create(
        [Finding(scan=scan, **{k: f.get(k, "") for k in FINDING_FIELDS})
         for f in ordered]
    )


def _progress_saver(scan):
    def cb(pct: int) -> None:
        scan.progress = max(scan.progress, int(pct))
        scan.save(update_fields=["progress"])

    return cb


# ---------------------------------------------------------------- mock ----

def _run_mock(scan) -> None:
    client = MockZapClient(scan.target.url, scan.config.scan_type)
    client.spider()  # exercise spider path; URLs discarded in mock
    scan.progress = 45
    scan.save(update_fields=["progress"])
    raw = client.active_scan()
    _persist_findings(scan, raw)
    _finish(scan)


# ---------------------------------------------------------------- real ----

def _ensure_daemon() -> None:
    """Guarantee a reachable daemon or raise with an actionable message."""
    from . import zap_process

    host = settings.SECURESCAN_ZAP_HOST
    port = settings.SECURESCAN_ZAP_PORT
    api_key = settings.SECURESCAN_ZAP_API_KEY
    if zap_process.zap_ready(host, port, api_key):
        return
    if not getattr(settings, "SECURESCAN_ZAP_AUTOSTART", False):
        raise RuntimeError(
            f"ZAP daemon not reachable at {host}:{port}. Start one "
            f"(python manage.py zap up, or set SECURESCAN_ZAP_AUTOSTART=1), "
            f"or run with SECURESCAN_MOCK=1."
        )
    zap_process.start_daemon(
        host, port, api_key, settings.SECURESCAN_ZAP_BOOT_TIMEOUT_S
    )


def _apply_auth_header(client: RealZapClient, scan) -> None:
    """Best-effort authenticated scan via the target's secret header."""
    name = (scan.target.secret_header_name or "").strip()
    if not name:
        return
    value = scan.target.secret_header_value_plain
    if not value:
        return
    if not client.set_auth_header(name, value):
        logger.warning(
            "Scan %s: could not register auth header via ZAP Replacer "
            "(add-on missing?); continuing unauthenticated.",
            scan.pk,
        )


def _run_real_local(scan) -> None:
    validate_scan_target(scan.target.url, resolve=True)
    _ensure_daemon()
    client = build_client(scan, progress_cb=_progress_saver(scan))
    _apply_auth_header(client, scan)
    client.new_session()
    raw = client.execute()
    _persist_findings(scan, raw)
    _finish(scan)


def _run_real_docker(scan, container_box: list) -> None:
    validate_scan_target(scan.target.url, resolve=True)
    import docker

    docker_client = docker.from_env()
    container = docker_client.containers.run(
        ZAP_IMAGE,
        command=(
            "zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.disablekey=true"
        ),
        detach=True,
        remove=False,
        mem_limit="1g",
        name=f"securescan-{scan.pk}",
        ports={"8080/tcp": ("127.0.0.1",)},
    )
    container_box.append(container)
    host_port = int(
        container.attrs["NetworkSettings"]["Ports"]["8080/tcp"][0]["HostPort"]
    )
    boot_timeout = settings.SECURESCAN_ZAP_BOOT_TIMEOUT_S
    deadline = time.monotonic() + boot_timeout
    while time.monotonic() < deadline:
        from . import zap_process

        if zap_process.zap_ready("127.0.0.1", host_port):
            break
        container.reload()
        if container.status in ("exited", "dead"):
            raise RuntimeError(
                f"ZAP container exited early (status={container.status})."
            )
        time.sleep(1.0)
    else:
        raise RuntimeError(f"ZAP container not ready within {boot_timeout}s.")
    client = RealZapClient(
        scan.target.url,
        scan.config.scan_type,
        host="127.0.0.1",
        port=host_port,
        scan_budget_s=settings.SECURESCAN_ZAP_SCAN_BUDGET_S,
        spider_depth=scan.config.spider_depth,
        max_pages=scan.config.max_pages,
        progress_cb=_progress_saver(scan),
    )
    _apply_auth_header(client, scan)
    client.new_session()
    raw = client.execute()
    _persist_findings(scan, raw)
    _finish(scan)


def seed_estimate(scan) -> None:
    cost, duration = estimate_cost(
        scan.config.max_pages, scan.config.spider_depth, scan.config.scan_type
    )
    scan.cost_estimate = cost
    scan.duration_estimate_s = duration
    scan.save(update_fields=["cost_estimate", "duration_estimate_s"])


__all__ = ["MOCK_FINDINGS", "MockZapClient", "run_scan", "seed_estimate"]
