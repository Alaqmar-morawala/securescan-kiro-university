"""Local ZAP daemon lifecycle: probe, autostart, reuse, stop.

The real engine needs a reachable ZAP daemon. On a host with the
``zaproxy`` binary installed this module can launch one in daemon mode
(bound to 127.0.0.1, logs under /tmp) and reuse it across scans —
subsequent scans connect to the already-running instance in milliseconds.

``stop_daemon`` only kills instances this module started (pidfile-tracked),
so a daemon the user launched manually is never touched.
"""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import time
from pathlib import Path


def find_zap_binary() -> str | None:
    for name in ("zaproxy", "zap.sh", "zap"):
        found = shutil.which(name)
        if found:
            return found
    return None


def zap_ready(host: str, port: int, api_key: str = "", timeout: float = 0.6) -> bool:
    """True when a ZAP daemon answers on host:port (cheap probe)."""
    try:
        import requests

        params = {"apikey": api_key} if api_key else None
        resp = requests.get(
            f"http://{host}:{int(port)}/JSON/core/view/version/",
            params=params,
            timeout=timeout,
        )
        return resp.ok and "version" in resp.json()
    except Exception:
        return False


def _pidfile(port: int) -> Path:
    return Path(f"/tmp/securescan-zap-{port}.pid")


def _logfile(port: int) -> Path:
    return Path(f"/tmp/securescan-zap-{port}.log")


def start_daemon(
    host: str = "127.0.0.1",
    port: int = 8090,
    api_key: str = "",
    boot_timeout_s: int = 240,
) -> bool:
    """Start a local daemon and wait until ready. Returns True when ready.

    No-op when a daemon already answers. Raises RuntimeError when the
    binary is missing, the process exits early, or boot exceeds the
    timeout (log path is included in the message).
    """
    if zap_ready(host, port, api_key):
        return True
    binary = find_zap_binary()
    if not binary:
        raise RuntimeError(
            "zaproxy binary not found on PATH; install it or point "
            "SECURESCAN_ZAP_HOST/PORT at an existing daemon."
        )
    cmd = [binary, "-daemon", "-host", host, "-port", str(port)]
    if api_key:
        cmd += ["-config", f"api.key={api_key}", "-config", "api.disablekey=false"]
    else:
        cmd += ["-config", "api.disablekey=true"]
    log_path = _logfile(port)
    with open(log_path, "ab") as log:
        proc = subprocess.Popen(
            cmd,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    _pidfile(port).write_text(str(proc.pid))
    deadline = time.monotonic() + boot_timeout_s
    while time.monotonic() < deadline:
        if zap_ready(host, port, api_key):
            return True
        if proc.poll() is not None:
            raise RuntimeError(
                f"ZAP daemon exited early (rc={proc.returncode}); see {log_path}"
            )
        time.sleep(1.0)
    raise RuntimeError(
        f"ZAP daemon not ready within {boot_timeout_s}s; see {log_path}"
    )


def stop_daemon(port: int = 8090, sig: int = signal.SIGTERM) -> bool:
    """Stop a daemon previously started by ``start_daemon`` (pidfile-tracked)."""
    pidfile = _pidfile(port)
    if not pidfile.exists():
        return False
    try:
        pid = int(pidfile.read_text().strip())
    except ValueError:
        pidfile.unlink(missing_ok=True)
        return False
    try:
        os.kill(pid, sig)
    except ProcessLookupError:
        pass
    pidfile.unlink(missing_ok=True)
    return True
