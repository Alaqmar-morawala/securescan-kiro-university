"""Example tests: auth, targets, estimate, mock scan run, PDF, history isolation."""

import pytest
from django.contrib.auth.models import User
from django.test import Client

from scanner.docker_runner import run_scan
from scanner.models import Scan, ScanConfig, Target
from scanner.services import estimate_cost


@pytest.fixture
def user(db):
    return User.objects.create_user("tester", password="pass12345")


@pytest.fixture
def client_user(client: Client, user):
    client.force_login(user)
    return client


def test_register_and_login(client: Client, db):
    r = client.post("/accounts/register/", {"username": "u1", "password1": "StrongPass!234", "password2": "StrongPass!234"})
    assert r.status_code in (200, 302)
    assert client.login(username="u1", password="StrongPass!234")


def test_add_target_validation(client_user: Client):
    r = client_user.post("/targets/add/", {"name": "t", "url": "ftp://bad.example/x"})
    assert r.status_code == 200  # form error, not redirect
    r = client_user.post("/targets/add/", {"name": "demo", "url": "https://example.com"})
    assert r.status_code == 302


def test_configure_and_estimate(client_user: Client, user):
    t = Target.objects.create(owner=user, name="demo", url="https://example.com")
    r = client_user.post(f"/targets/{t.pk}/configure/", {"scan_type": "full", "spider_depth": 3, "max_pages": 100})
    assert r.status_code == 302
    scan = Scan.objects.filter(owner=user).latest("created_at")
    cost, dur = estimate_cost(100, 3, "full")
    assert scan.cost_estimate == cost and scan.duration_estimate_s == dur


def test_mock_scan_run_and_pdf(client_user: Client, user):
    t = Target.objects.create(owner=user, name="demo", url="https://example.com")
    cfg = ScanConfig.objects.create(target=t, scan_type="full", spider_depth=2, max_pages=20)
    scan = Scan.objects.create(owner=user, target=t, config=cfg)
    run_scan(scan)
    scan.refresh_from_db()
    assert scan.status == "DONE" and scan.findings.count() >= 3
    r = client_user.get(f"/scans/{scan.pk}/report.pdf")
    assert r.status_code == 200 and r["Content-Type"] == "application/pdf"
    assert r.content[:4] == b"%PDF"


def test_history_isolation(client: Client, db):
    u1 = User.objects.create_user("u1", password="x12345678")
    u2 = User.objects.create_user("u2", password="x12345678")
    for u in (u1, u2):
        t = Target.objects.create(owner=u, name="t", url="https://example.com")
        c = ScanConfig.objects.create(target=t)
        Scan.objects.create(owner=u, target=t, config=c)
    client.force_login(u1)
    r = client.get("/history/")
    assert r.status_code == 200
    scans = list(r.context["scans"])
    assert scans and all(s.owner == u1 for s in scans)
