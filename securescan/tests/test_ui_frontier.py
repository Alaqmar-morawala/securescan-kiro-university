"""End-to-end frontier tests: the exact journey a judge follows.

register -> add website -> configure -> start scan -> detail page shows
severity-ordered findings -> HTML/PDF reports render -> history lists it.

Also locks the UI polling contract (progress JSON + auto-refresh hook),
cross-user isolation (404s), and PDF auth gating.
"""

import pytest
from django.contrib.auth.models import User

from scanner.docker_runner import run_scan
from scanner.models import Scan, ScanConfig, Target


def _make_user(name):
    return User.objects.create_user(name, password="StrongPass!234")


def _flow_to_done(client):
    """Drive register -> target -> configure -> start; return the DONE scan."""
    r = client.post(
        "/accounts/register/",
        {
            "username": "e2e",
            "password1": "StrongPass!234",
            "password2": "StrongPass!234",
        },
    )
    assert r.status_code in (200, 302)
    r = client.post(
        "/targets/add/", {"name": "demo", "url": "https://example.com"}
    )
    assert r.status_code == 302
    target = Target.objects.get(name="demo")
    r = client.post(
        f"/targets/{target.pk}/configure/",
        {"scan_type": "full", "spider_depth": 2, "max_pages": 20},
    )
    assert r.status_code == 302
    scan = Scan.objects.filter(owner__username="e2e").latest("created_at")
    r = client.post(f"/scans/{scan.pk}/start/")
    assert r.status_code == 302
    scan.refresh_from_db()
    assert scan.status == "DONE"
    return scan


@pytest.mark.django_db
def test_full_user_flow_smoke(client):
    scan = _flow_to_done(client)
    assert scan.findings.count() >= 3

    r = client.get(f"/scans/{scan.pk}/")
    assert r.status_code == 200
    body = r.content.decode()
    for sev in ("High", "Medium", "Low", "Info"):
        assert sev in body

    r = client.get(f"/scans/{scan.pk}/report.html")
    assert r.status_code == 200

    r = client.get(f"/scans/{scan.pk}/report.pdf")
    assert r.status_code == 200
    assert r["Content-Type"] == "application/pdf"
    assert r.content[:4] == b"%PDF"

    r = client.get("/history/")
    assert r.status_code == 200
    assert str(scan.pk) in r.content.decode()


@pytest.mark.django_db
def test_detail_shows_severity_order(client):
    scan = _flow_to_done(client)
    r = client.get(f"/scans/{scan.pk}/")
    assert r.status_code == 200
    ordered = [f.severity for f in r.context["findings"]]
    assert ordered == ["High", "High", "Medium", "Low", "Info"]
    body = r.content.decode()
    positions = [
        body.find("sev-" + s) for s in ("high", "medium", "low", "info")
    ]
    assert all(p >= 0 for p in positions), "severity badges missing"
    assert positions == sorted(positions), "badges out of severity order"


@pytest.mark.django_db
def test_progress_endpoint_contract(client):
    scan = _flow_to_done(client)
    r = client.get(f"/scans/{scan.pk}/progress/")
    assert r.status_code == 200
    data = r.json()
    assert data == {"status": "DONE", "progress": 100}
    # Detail page must wire the auto-refresh hook to this endpoint.
    r = client.get(f"/scans/{scan.pk}/")
    assert r.status_code == 200
    body = r.content.decode()
    assert f"/scans/{scan.pk}/progress/" in body
    assert "data-progress-url" in body


@pytest.mark.django_db
def test_cross_user_isolation_404s(client):
    scan = _flow_to_done(client)
    client.logout()
    _make_user("intruder")
    assert client.login(username="intruder", password="StrongPass!234")
    for url in (
        f"/scans/{scan.pk}/",
        f"/scans/{scan.pk}/progress/",
        f"/scans/{scan.pk}/report.html",
        f"/scans/{scan.pk}/report.pdf",
    ):
        assert client.get(url).status_code == 404, url


@pytest.mark.django_db
def test_pdf_requires_login(client):
    u = _make_user("owner")
    t = Target.objects.create(owner=u, name="t", url="https://example.com")
    c = ScanConfig.objects.create(target=t)
    scan = Scan.objects.create(owner=u, target=t, config=c)
    run_scan(scan)
    client.logout()
    r = client.get(f"/scans/{scan.pk}/report.pdf")
    assert r.status_code == 302
    assert "/accounts/login/" in r["Location"]
