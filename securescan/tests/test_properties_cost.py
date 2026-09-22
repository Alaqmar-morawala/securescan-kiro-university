"""Property P1: cost estimate monotonic in (pages, depth) for fixed scan type.

Kiro PBT lesson (guide-4-property-testing): general rule that must always hold,
checked over hundreds of generated inputs instead of single examples.
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from scanner.services import SCAN_WEIGHTS, estimate_cost


@given(
    pages1=st.integers(0, 500),
    pages2=st.integers(0, 500),
    depth1=st.integers(0, 5),
    depth2=st.integers(0, 5),
    scan_type=st.sampled_from(sorted(SCAN_WEIGHTS)),
)
@settings(max_examples=150)
def test_cost_monotonic(pages1, pages2, depth1, depth2, scan_type):
    c1, d1 = estimate_cost(min(pages1, pages2), min(depth1, depth2), scan_type)
    c2, d2 = estimate_cost(max(pages1, pages2), max(depth1, depth2), scan_type)
    assert c1 <= c2
    assert d1 <= d2


@given(scan_type=st.sampled_from(sorted(SCAN_WEIGHTS)))
@settings(max_examples=50)
def test_scan_type_weight_ordering(scan_type):
    costs = {t: estimate_cost(50, 2, t)[0] for t in SCAN_WEIGHTS}
    order = ["baseline", "spider", "active", "full"]
    vals = [costs[t] for t in order]
    assert vals == sorted(vals)
