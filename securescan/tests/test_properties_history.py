"""Property P3: scan history newest-first invariant + owner isolation."""

import pytest
from django.contrib.auth.models import User

from scanner.models import Scan, ScanConfig, Target


@pytest.mark.django_db
def test_history_ordering_newest_first():
    u = User.objects.create_user("hist", password="x12345678")
    t = Target.objects.create(owner=u, name="t", url="https://example.com")
    c = ScanConfig.objects.create(target=t)
    ids = [Scan.objects.create(owner=u, target=t, config=c).pk for _ in range(5)]
    qs = list(Scan.objects.filter(owner=u).order_by("-created_at"))
    assert [s.pk for s in qs] == sorted(ids, reverse=True)
    assert qs == sorted(qs, key=lambda s: s.created_at, reverse=True)
