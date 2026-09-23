"""Property P3: scan history newest-first invariant + owner isolation.

Kiro PBT lesson (guide-4-property-testing): general rule that must always hold,
checked over hundreds of generated inputs instead of single examples.
"""

import datetime
import uuid

import pytest
from django.contrib.auth.models import User
from hypothesis import given, settings
from hypothesis import strategies as st

from scanner.models import Scan, ScanConfig, Target


@pytest.mark.django_db
def test_history_ordering_newest_first():
    u = User.objects.create_user("hist", password="x12345678")
    t = Target.objects.create(owner=u, name="t", url="https://example.com")
    c = ScanConfig.objects.create(target=t)
    ids = [
        Scan.objects.create(owner=u, target=t, config=c).pk for _ in range(5)
    ]
    qs = list(Scan.objects.filter(owner=u).order_by("-created_at"))
    assert [s.pk for s in qs] == sorted(ids, reverse=True)
    assert qs == sorted(qs, key=lambda s: s.created_at, reverse=True)


@pytest.mark.django_db
@settings(max_examples=100, deadline=None)
@given(
    stamps=st.lists(
        st.datetimes(
            min_value=datetime.datetime(2020, 1, 1),
            max_value=datetime.datetime(2030, 1, 1),
            timezones=st.just(datetime.timezone.utc),
        ),
        min_size=1,
        max_size=3,
        unique=True,
    ),
)
def test_history_newest_first_property(stamps):
    tag = uuid.uuid4().hex[:12]
    u = User.objects.create_user(f"p3_{tag}", password="x12345678")
    other = User.objects.create_user(
        f"p3_{tag}_other", password="x12345678"
    )
    t = Target.objects.create(owner=u, name="t", url="https://example.com")
    c = ScanConfig.objects.create(target=t)
    to = Target.objects.create(
        owner=other, name="t", url="https://example.com"
    )
    co = ScanConfig.objects.create(target=to)
    Scan.objects.create(owner=other, target=to, config=co)  # must not leak
    for dt in stamps:
        s = Scan.objects.create(owner=u, target=t, config=c)
        Scan.objects.filter(pk=s.pk).update(created_at=dt)
    qs = list(Scan.objects.filter(owner=u).order_by("-created_at"))
    assert [s.created_at for s in qs] == sorted(stamps, reverse=True)
    assert all(s.owner_id == u.pk for s in qs)
