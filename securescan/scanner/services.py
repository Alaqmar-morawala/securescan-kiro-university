"""Cost estimation + scan orchestration services."""

from decimal import Decimal

SCAN_WEIGHTS = {"baseline": 1, "spider": 2, "active": 4, "full": 6}
BASE_COST = Decimal("0.50")
PER_UNIT = Decimal("0.02")
BASE_SECONDS = 20


def estimate_cost(
    pages: int, depth: int, scan_type: str
) -> tuple[Decimal, int]:
    """Return (cost, duration_seconds).

    Property P1: monotonic non-decreasing in pages and depth for a fixed type.
    """
    pages = max(0, int(pages))
    depth = max(0, min(5, int(depth)))
    weight = SCAN_WEIGHTS.get(scan_type, 1)
    units = pages * (depth + 1) * weight
    cost = BASE_COST + Decimal(units) * PER_UNIT
    duration = BASE_SECONDS + units * 2
    return (cost.quantize(Decimal("0.01")), int(duration))


SEVERITY_RANK = {"High": 4, "Medium": 3, "Low": 2, "Info": 1}


def order_findings(findings: list[dict]) -> list[dict]:
    """Sort findings by severity High > Medium > Low > Info, then name."""
    return sorted(
        findings,
        key=lambda f: (
            -SEVERITY_RANK.get(f.get("severity", "Info"), 0),
            f.get("name", ""),
        ),
    )
