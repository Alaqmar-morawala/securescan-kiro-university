"""Smoke test: cost-service sanity.

Referenced by .kiro/hooks/python-checks.json post-save hook.
"""

from scanner.services import estimate_cost


def test_smoke_estimate_cost():
    cost, duration = estimate_cost(50, 2, "full")
    assert cost > 0
    assert duration > 0
