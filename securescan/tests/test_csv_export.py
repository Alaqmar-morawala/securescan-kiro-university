"""CSV export (task 11): auth, ownership, format."""

import csv
import io

import pytest
from django.contrib.auth.models import User

from scanner.docker_runner import run_scan
from scanner.models import Scan, ScanConfig, Target


@pytest.fixture
def done_scan(db):
    user = User.objects.create_user("csv-owner", password="x12345678")
    target = Target.objects.create(owner=user, name="t", url="https://example.com")
    config = ScanConfig.objects.create(target=target, scan_type="full")
    scan = Scan.objects.create(owner=user, target=target, config=config)
    run_scan(scan)
    scan.refresh_from_db()
    assert scan.status == "DONE"
    return scan


def test_csv_export_content(client, done_scan):
    client.force_login(done_scan.owner)
    r = client.get(f"/scans/{done_scan.pk}/report.csv")
    assert r.status_code == 200
    assert r["Content-Type"] == "text/csv"
    assert "attachment" in r["Content-Disposition"]
    rows = list(csv.reader(io.StringIO(r.content.decode())))
    assert rows[0] == ["Severity", "Finding", "URL", "CWE", "Description", "Solution"]
    assert len(rows) == 1 + done_scan.findings.count()
    body = "\n".join(r.content.decode().splitlines())
    assert str(done_scan.findings.first().name) in body


def test_csv_requires_login(client, done_scan):
    r = client.get(f"/scans/{done_scan.pk}/report.csv")
    assert r.status_code == 302
    assert "/accounts/login/" in r["Location"]


def test_csv_cross_user_404(client, done_scan):
    User.objects.create_user("intruder", password="x12345678")
    client.force_login(User.objects.get(username="intruder"))
    assert client.get(f"/scans/{done_scan.pk}/report.csv").status_code == 404
