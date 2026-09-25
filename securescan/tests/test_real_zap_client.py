"""RealZapClient behaviour against an in-process fake ZAP API."""

import pytest

from scanner.zap_client import RealZapClient, map_alert

from .fake_zap import ALERTS, FakeZap, FakeZapServer

TARGET = "http://target.example/"


@pytest.fixture
def fake_zap():
    return FakeZap()


@pytest.fixture
def zap_server(fake_zap):
    with FakeZapServer(fake_zap) as server:
        yield server


def make_client(server, **kwargs):
    defaults = dict(
        scan_type="full",
        host="127.0.0.1",
        port=server.port,
        request_timeout=5,
        poll_interval_s=0.01,
    )
    defaults.update(kwargs)
    return RealZapClient(TARGET, **defaults)


def test_execute_full_flow_maps_alerts(zap_server):
    client = make_client(zap_server)
    findings = client.execute()

    assert [f["severity"] for f in findings] == ["High", "Low", "Info"]
    assert findings[0]["name"] == "Cross Site Scripting (Reflected)"
    assert findings[0]["cwe"] == "CWE-79"
    assert findings[1]["cwe"] == "CWE-16"
    assert findings[2]["cwe"] == ""  # no cweid -> empty, never "CWE-"
    # spider results were fetched and the session was reset first
    paths = [p for p, _ in zap_server.fake.requests]
    assert paths.index("/JSON/core/action/newSession/") < paths.index(
        "/JSON/spider/action/scan/"
    )
    assert "/JSON/spider/view/results/" in paths


def test_progress_callbacks_monotonic_and_bounded(zap_server):
    seen = []
    client = make_client(zap_server, progress_cb=seen.append)
    client.execute()
    assert seen
    assert all(0 <= p <= 100 for p in seen)
    assert seen == sorted(seen)
    assert seen[-1] == 92  # alerts-fetch marker; runner sets 100 on DONE


def test_api_key_enforced(zap_server):
    fake_zap = FakeZap(api_key="sekrit")
    with FakeZapServer(fake_zap) as server:
        import requests

        client = make_client(server, api_key="wrong")
        with pytest.raises(requests.HTTPError):
            client.version()


def test_retries_on_502(fake_zap):
    fake_zap.fail_version_once = True
    with FakeZapServer(fake_zap) as server:
        client = make_client(server)
        assert client.version() == "2.17.0-fake"


def test_auth_header_rule_add_and_clear(zap_server):
    client = make_client(zap_server)
    assert client.set_auth_header("X-Auth", "token-123")
    rule = zap_server.fake.auth_rules[-1]
    assert rule["matchtype"] == "REQ_HEADER"
    assert rule["match"] == "X-Auth"
    assert rule["replacement"] == "token-123"
    client.clear_auth_header()
    assert zap_server.fake.removed_rules


def test_scan_budget_exceeded():
    client = RealZapClient(
        TARGET, "full", host="127.0.0.1", port=1, scan_budget_s=0,
        poll_interval_s=0.01,
    )
    with pytest.raises(RuntimeError, match="budget"):
        client.execute()


def test_baseline_skips_active_scan(zap_server):
    client = make_client(zap_server, scan_type="baseline")
    client.execute()
    paths = [p for p, _ in zap_server.fake.requests]
    assert "/JSON/ascan/action/scan/" not in paths
    assert "/JSON/spider/action/scan/" not in paths


def test_map_alert_risk_normalisation():
    # ZAP 2.17+ string risk names and legacy numeric codes both map.
    assert map_alert({"alert": "A", "risk": "High", "cweid": "89"})["severity"] == "High"
    assert map_alert({"alert": "A", "risk": "Medium", "cweid": "x!"})["severity"] == "Medium"
    assert map_alert({"alert": "A", "risk": "informational"})["severity"] == "Info"
    assert map_alert({"alert": "A", "risk": "1"})["severity"] == "Low"
    assert map_alert({"alert": "A", "risk": None})["severity"] == "Info"
    assert map_alert({"alert": "A", "risk": "garbage"})["severity"] == "Info"
    assert map_alert({"alert": "A" * 500, "risk": 1})["name"] == "A" * 200
    long_url = map_alert({"alert": "A", "url": "http://x/" + "p" * 600})["url"]
    assert len(long_url) <= 500
    assert {a["risk"] for a in ALERTS} == {"High", "1", "Informational"}
