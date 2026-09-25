"""Engine selection + run_scan wiring (mock/real/auto, injected plans)."""

import pytest
from django.contrib.auth.models import User
from django.test import override_settings

from scanner.docker_runner import run_scan
from scanner.engine import (
    EnginePlan,
    clear_status_cache,
    engine_status_cached,
    resolve_engine,
)
from scanner.models import Scan, ScanConfig, Target


def _make_scan(user):
    target = Target.objects.create(owner=user, name="t", url="https://example.com")
    config = ScanConfig.objects.create(target=target, scan_type="full")
    return Scan.objects.create(owner=user, target=target, config=config)


@pytest.mark.django_db
def test_forced_mock_via_settings():
    with override_settings(SECURESCAN_MOCK=True):
        plan = resolve_engine(zap_alive=lambda: True)
    assert plan.mode == "mock"  # explicit setting beats the probe


@pytest.mark.django_db
def test_forced_real_ignores_probe():
    with override_settings(SECURESCAN_MOCK=False):
        plan = resolve_engine(zap_alive=lambda: False)
    assert plan.is_real


def test_auto_falls_back_without_daemon():
    with override_settings(SECURESCAN_MOCK=None):
        plan = resolve_engine(zap_alive=lambda: False)
    assert plan.mode == "mock"
    assert "daemon" in plan.reason


def test_auto_picks_real_when_daemon_up():
    with override_settings(SECURESCAN_MOCK=None):
        plan = resolve_engine(zap_alive=lambda: True)
    assert plan.is_real


def test_status_cache_hits_probe_once(monkeypatch):
    clear_status_cache()
    calls = []

    def probe():
        calls.append(1)
        return False

    monkeypatch.setattr("scanner.engine._zap_alive", probe)
    with override_settings(SECURESCAN_MOCK=None):
        engine_status_cached()
        engine_status_cached()
    assert len(calls) == 1
    clear_status_cache()


@pytest.mark.django_db
def test_run_scan_injected_mock_plan(user=None):
    user = User.objects.create_user("eng-user", password="x12345678")
    scan = _make_scan(user)
    run_scan(scan, engine=EnginePlan("mock", "test"))
    scan.refresh_from_db()
    assert scan.status == "DONE"
    assert scan.findings.count() >= 3


@pytest.mark.django_db
def test_run_scan_real_without_daemon_fails_actionably():
    user = User.objects.create_user("eng-user2", password="x12345678")
    scan = _make_scan(user)
    # Port 1 refuses instantly; autostart off -> actionable RuntimeError.
    with override_settings(
        SECURESCAN_MOCK=False,
        SECURESCAN_ZAP_PORT=1,
        SECURESCAN_ZAP_AUTOSTART=False,
    ):
        run_scan(scan, engine=EnginePlan("real", "forced by test"))
    scan.refresh_from_db()
    assert scan.status == "FAILED"
    assert "not reachable" in scan.error
