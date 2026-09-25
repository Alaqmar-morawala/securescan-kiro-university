"""Engine selection: mock fixtures vs the real ZAP engine.

``resolve_engine`` returns an :class:`EnginePlan` describing what
``run_scan`` will do:

* ``settings.SECURESCAN_MOCK is True``  -> mock (offline demo, judged path)
* ``settings.SECURESCAN_MOCK is False`` -> real (scan FAILS if unreachable)
* ``None`` (``SECURESCAN_MOCK=auto``)   -> real if a ZAP daemon answers,
  otherwise mock, with the reason surfaced in the UI engine chip.

The reachability probe is cached briefly so the per-request UI status
check stays cheap when no daemon is running.
"""

from __future__ import annotations

import time

from dataclasses import dataclass

from django.conf import settings


@dataclass(frozen=True)
class EnginePlan:
    mode: str  # "mock" | "real"
    reason: str

    @property
    def is_real(self) -> bool:
        return self.mode == "real"

    @property
    def label(self) -> str:
        return "Live ZAP engine" if self.is_real else "Demo fixtures"


def _zap_alive() -> bool:
    from . import zap_process

    return zap_process.zap_ready(
        settings.SECURESCAN_ZAP_HOST,
        settings.SECURESCAN_ZAP_PORT,
        settings.SECURESCAN_ZAP_API_KEY,
    )


def resolve_engine(*, zap_alive=None) -> EnginePlan:
    """Decide the engine for the current configuration.

    ``zap_alive`` is injectable for tests; by default a real probe runs.
    """
    mock = getattr(settings, "SECURESCAN_MOCK", None)
    if mock is True:
        return EnginePlan(
            "mock", "SECURESCAN_MOCK=1: deterministic fixtures (offline)."
        )
    if mock is False:
        return EnginePlan("real", "SECURESCAN_MOCK=0: real ZAP required.")
    probe = _zap_alive if zap_alive is None else zap_alive
    if probe():
        return EnginePlan("real", "Auto: ZAP daemon reachable.")
    return EnginePlan(
        "mock", "Auto: no ZAP daemon reachable — running demo fixtures."
    )


_cache: tuple[float, EnginePlan] | None = None
_CACHE_SECONDS = 15.0


def engine_status_cached() -> EnginePlan:
    """Cached variant for the per-request UI context processor."""
    global _cache
    now = time.monotonic()
    if _cache is not None and now - _cache[0] < _CACHE_SECONDS:
        return _cache[1]
    plan = resolve_engine()
    _cache = (now, plan)
    return plan


def clear_status_cache() -> None:
    global _cache
    _cache = None


def build_client(scan, progress_cb=None):
    """Construct the real-engine client for a scan from settings."""
    from .zap_client import RealZapClient

    return RealZapClient(
        scan.target.url,
        scan.config.scan_type,
        host=settings.SECURESCAN_ZAP_HOST,
        port=settings.SECURESCAN_ZAP_PORT,
        api_key=settings.SECURESCAN_ZAP_API_KEY,
        scan_budget_s=settings.SECURESCAN_ZAP_SCAN_BUDGET_S,
        spider_depth=scan.config.spider_depth,
        max_pages=scan.config.max_pages,
        progress_cb=progress_cb,
    )
