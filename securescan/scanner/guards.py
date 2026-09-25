"""Scan-target guard: SSRF / private-network protection.

The real engine fetches user-supplied URLs. Without a guard, a user could
point SecureScan at internal services — cloud metadata endpoints, loopback
admin panels, RFC1918 hosts. Rules enforced by ``validate_scan_target``:

* http/https schemes only
* literal IPs must be globally routable (blocks 127.0.0.1, ::1,
  169.254.169.254, RFC1918, CGNAT, documentation ranges, ... —
  ``ipaddress.is_global`` covers all of these)
* ``localhost`` / ``*.localhost`` / ``*.local`` / ``*.internal`` hostnames
  blocked
* hostnames are resolved and *every* resolved address must be global

Known, documented limitation: the hostname is re-resolved at fetch time by
ZAP, so DNS rebinding between this check and the fetch is theoretically
possible on a hostile resolver. Acceptable for a single-tenant, self-hosted
deployment; do not run the real engine on shared infrastructure.

``SECURESCAN_ALLOW_PRIVATE_TARGETS=1`` disables the private-address checks
so the bundled vulnerable demo target (``manage.py vuln_target``) and local
test apps can be scanned. Local development ONLY.
"""

from __future__ import annotations

import ipaddress
import os
import socket
from urllib.parse import urlsplit


class TargetNotAllowed(ValueError):
    """Raised when a scan target fails the SSRF/private-network guard."""


_BLOCKED_HOST_SUFFIXES = (".localhost", ".local", ".internal")


def _allow_private() -> bool:
    # Read from the environment (not settings) so tests and one-off runs can
    # flip it per-process without reloading Django.
    return os.environ.get(
        "SECURESCAN_ALLOW_PRIVATE_TARGETS", ""
    ).strip().lower() in ("1", "true", "yes", "on")


def _require_global(addr: ipaddress._BaseAddress) -> None:
    if not addr.is_global:
        raise TargetNotAllowed(
            f"Blocked: {addr} is not a publicly routable address. "
            "Set SECURESCAN_ALLOW_PRIVATE_TARGETS=1 only for local demos."
        )


def validate_scan_target(url: str, *, resolve: bool = True) -> str:
    """Validate a scan target URL; return the trimmed URL or raise.

    ``resolve=False`` performs only static checks (scheme, hostname shape,
    literal IPs) — used by the form so validation never needs DNS.
    Full resolution happens again at scan time (defense in depth).
    """
    url = (url or "").strip()
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https"):
        raise TargetNotAllowed("Only http:// and https:// targets can be scanned.")
    host = parts.hostname
    if not host:
        raise TargetNotAllowed("Target URL has no hostname.")
    if _allow_private():
        return url

    host_l = host.lower()
    if host_l == "localhost" or host_l.endswith(_BLOCKED_HOST_SUFFIXES):
        raise TargetNotAllowed(f"Blocked: '{host_l}' is a local/internal name.")

    try:
        literal = ipaddress.ip_address(host_l)
    except ValueError:
        literal = None
    if literal is not None:
        _require_global(literal)
        return url

    if resolve:
        try:
            infos = socket.getaddrinfo(host, None)
        except OSError as exc:
            raise TargetNotAllowed(f"Cannot resolve target host '{host}'.") from exc
        addrs = set()
        for info in infos:
            try:
                addrs.add(ipaddress.ip_address(info[4][0]))
            except ValueError:  # pragma: no cover - malformed resolver reply
                continue
        if not addrs:
            raise TargetNotAllowed(f"Cannot resolve target host '{host}'.")
        for addr in addrs:
            _require_global(addr)
    return url
