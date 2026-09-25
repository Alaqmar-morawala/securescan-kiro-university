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


# --- edge properties (task 11: estimate edge PBT) ---------------------------


@given(
    pages=st.integers(-50, 2000),
    depth=st.integers(-5, 50),
    scan_type=st.sampled_from(sorted(SCAN_WEIGHTS) + ["nonsense"]),
)
@settings(max_examples=200)
def test_edge_inputs_clamped_and_finite(pages, depth, scan_type):
    """Out-of-domain inputs are clamped/defaults, never crash or go negative."""
    cost, duration = estimate_cost(pages, depth, scan_type)
    assert cost >= 0
    assert duration >= 0
    assert cost == cost.quantize(__import__("decimal").Decimal("0.01"))
    # depth clamps to 0..5 regardless of input
    clamped_depth = max(0, min(5, max(0, depth)))
    clamped_pages = max(0, pages)
    expected_cost, expected_duration = estimate_cost(
        clamped_pages, clamped_depth, scan_type
    )
    assert (cost, duration) == (expected_cost, expected_duration)


@given(pages=st.integers(1, 1000), depth=st.integers(0, 5))
@settings(max_examples=100)
def test_duration_formula_matches_cost_units(pages, depth):
    from scanner.services import BASE_SECONDS, SCAN_WEIGHTS

    cost, duration = estimate_cost(pages, depth, "full")
    units = pages * (depth + 1) * SCAN_WEIGHTS["full"]
    assert duration == BASE_SECONDS + units * 2


@given(
    pages=st.integers(1, 1000),
    depth=st.integers(0, 5),
    base_pages=st.integers(1, 1000),
    base_depth=st.integers(0, 5),
)
@settings(max_examples=100)
def test_weight_ordering_any_volume(pages, depth, base_pages, base_depth):
    """full >= active >= spider >= baseline for the same (pages, depth), and
    each type is monotonic across volumes."""
    order = ["baseline", "spider", "active", "full"]
    at_target = [estimate_cost(pages, depth, t)[0] for t in order]
    assert at_target == sorted(at_target)
    at_base = [estimate_cost(base_pages, base_depth, t)[0] for t in order]
    assert at_base == sorted(at_base)
