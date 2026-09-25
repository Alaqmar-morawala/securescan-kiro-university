"""Opt-in integration test: a REAL scan against a REAL ZAP daemon.

Not part of the offline suite — run explicitly on a host with ZAP:

    RUN_ZAP_E2E=1 pytest tests/test_real_zap_integration.py -v

Starts the bundled vulnerable demo target on an ephemeral loopback port,
starts (or reuses) a local ZAP daemon, runs a full spider + active scan and
asserts real alerts come back with valid severities.
"""

import os
import threading

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_ZAP_E2E") != "1",
    reason="opt-in real-ZAP integration: set RUN_ZAP_E2E=1",
)

pytest.importorskip("requests")

from scanner import zap_process  # noqa: E402
from scanner.zap_client import RealZapClient  # noqa: E402


@pytest.fixture(scope="module")
def vuln_target():
    import django

    django.setup()
    os.environ["SECURESCAN_ALLOW_PRIVATE_TARGETS"] = "1"
    from scanner.management.commands.vuln_target import make_server

    httpd = make_server("127.0.0.1", 0)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}/"
    httpd.shutdown()
    httpd.server_close()


@pytest.fixture(scope="module")
def zap_daemon(vuln_target):
    host = os.environ.get("SECURESCAN_ZAP_HOST", "127.0.0.1")
    port = int(os.environ.get("SECURESCAN_ZAP_PORT", "8090"))
    api_key = os.environ.get("SECURESCAN_ZAP_API_KEY", "")
    if not zap_process.zap_ready(host, port, api_key):
        zap_process.start_daemon(
            host, port, api_key, boot_timeout_s=int(
                os.environ.get("SECURESCAN_ZAP_BOOT_TIMEOUT_S", "300")
            )
        )
    return host, port, api_key


def test_real_zap_scan_finds_real_issues(vuln_target, zap_daemon):
    host, port, api_key = zap_daemon
    client = RealZapClient(
        vuln_target,
        "full",
        host=host,
        port=port,
        api_key=api_key,
        poll_interval_s=0.5,
        scan_budget_s=900,
        spider_depth=2,
        max_pages=20,
    )
    assert "2." in client.version()  # real daemon answers

    findings = client.execute()
    names = [f["name"] for f in findings]
    assert findings, "real ZAP returned no alerts for the vulnerable target"
    assert all(f["severity"] in ("High", "Medium", "Low", "Info") for f in findings)

    lowered = " | ".join(names).lower()
    expected_markers = (
        "x-content-type-options",
        "content security policy",
        "scripting",
        "cookie",
        "server",
    )
    assert any(marker in lowered for marker in expected_markers), names
