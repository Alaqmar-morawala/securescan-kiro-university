"""Template context: which scan engine is active (for the UI status chip)."""

from . import engine


def scan_engine(request):
    plan = engine.engine_status_cached()
    return {
        "scan_engine": {
            "mode": plan.mode,
            "label": plan.label,
            "reason": plan.reason,
        }
    }
