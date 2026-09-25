"""OWASP ZAP client: real REST engine + deterministic mock for dev/tests/demo.

``RealZapClient`` drives a running ZAP daemon over its REST API: session
reset, optional authenticated-scan header (Replacer add-on), spider with
depth/page budgets, passive-scan drain, active scan, paginated alert
collection. Connection retries, poll deadlines and progress callbacks make
it safe for the background scan runner.
"""

from __future__ import annotations

import time


def _requests():
    """Import ``requests`` lazily.

    Mock mode (`SECURESCAN_MOCK=1`) never touches the network, so importing
    this module must not require the dependency. Only the real engine path
    needs it.
    """
    try:
        import requests
    except ImportError as exc:  # pragma: no cover - real ZAP path only
        raise RuntimeError(
            "The real ZAP engine requires the 'requests' package "
            "(pip install requests). Mock mode does not need it."
        ) from exc
    return requests


MOCK_FINDINGS = [
    {
        "name": "Cross-Site Scripting (Reflected)",
        "severity": "High",
        "url": "https://target.example/search?q=",
        "description": "Reflected input without output encoding.",
        "solution": "Encode output, validate input, deploy CSP.",
        "cwe": "CWE-79",
    },
    {
        "name": "SQL Injection",
        "severity": "High",
        "url": "https://target.example/item?id=",
        "description": "Unsanitized parameter concatenated into query.",
        "solution": "Use parameterized queries / ORM.",
        "cwe": "CWE-89",
    },
    {
        "name": "Missing Security Headers",
        "severity": "Medium",
        "url": "https://target.example/",
        "description": "X-Content-Type-Options / CSP missing.",
        "solution": "Add recommended security headers.",
        "cwe": "CWE-693",
    },
    {
        "name": "Cookie Without Secure Flag",
        "severity": "Low",
        "url": "https://target.example/",
        "description": "Session cookie missing Secure flag.",
        "solution": "Set Secure + HttpOnly + SameSite.",
        "cwe": "CWE-614",
    },
    {
        "name": "Server Version Disclosure",
        "severity": "Info",
        "url": "https://target.example/",
        "description": "Banner leaks server version.",
        "solution": "Suppress verbose banners.",
        "cwe": "CWE-200",
    },
]


class MockZapClient:
    """Deterministic stand-in: no network, no Docker."""

    def __init__(self, target_url: str, scan_type: str = "baseline"):
        self.target_url = target_url
        self.scan_type = scan_type

    def spider(self) -> list[str]:
        base = self.target_url.rstrip("/")
        return [base + "/", base + "/about", base + "/contact"]

    def active_scan(self) -> list[dict]:
        findings = [
            dict(
                f,
                url=f["url"].replace(
                    "https://target.example",
                    self.target_url.rstrip("/"),
                ),
            )
            for f in MOCK_FINDINGS
        ]
        if self.scan_type == "baseline":
            return [f for f in findings if f["severity"] in ("High", "Medium")]
        return findings


# ZAP alert "risk" field: numeric codes (older builds: 0=Info .. 3=High) or
# string names (2.17+: "Informational"/"Low"/"Medium"/"High").
_RISK_TO_SEVERITY = {3: "High", 2: "Medium", 1: "Low", 0: "Info"}
_RISK_NAMES = {
    "high": "High", "3": "High",
    "medium": "Medium", "2": "Medium",
    "low": "Low", "1": "Low",
    "informational": "Info", "info": "Info", "0": "Info",
}


def _map_risk(value) -> str:
    if value is None:
        return "Info"
    name = _RISK_NAMES.get(str(value).strip().lower())
    if name:
        return name
    try:
        return _RISK_TO_SEVERITY.get(int(str(value).strip()), "Info")
    except ValueError:
        return "Info"


def map_alert(alert: dict) -> dict:
    """Map a raw ZAP alert JSON object to a Finding-compatible dict."""
    cwe = str(alert.get("cweid") or "").strip()
    return {
        "name": (alert.get("alert") or "Unknown alert")[:200],
        "severity": _map_risk(alert.get("risk")),
        "url": (alert.get("url") or "")[:500],
        "description": alert.get("description") or "",
        "solution": alert.get("solution") or "",
        "cwe": f"CWE-{cwe}" if cwe.isdigit() else "",
    }


class RealZapClient:
    """Drive a running OWASP ZAP daemon over its REST API.

    Scan-type semantics:
      * ``baseline`` — fetch the target and wait for passive rules only
      * ``spider``   — crawl (respecting depth/page budget) + passive rules
      * ``active`` / ``full`` — crawl + passive + active rules
    """

    AUTH_RULE_DESCRIPTION = "securescan-auth-header"

    def __init__(
        self,
        target_url: str,
        scan_type: str = "full",
        *,
        host: str = "127.0.0.1",
        port: int = 8090,
        api_key: str = "",
        request_timeout: float = 30,
        scan_budget_s: int = 1800,
        poll_interval_s: float = 1.0,
        spider_depth: int | None = None,
        max_pages: int | None = None,
        progress_cb=None,
    ):
        self.target_url = target_url.rstrip("/")
        self.scan_type = scan_type
        self.base = f"http://{host}:{int(port)}"
        self.api_key = api_key
        self.request_timeout = request_timeout
        self.scan_budget_s = scan_budget_s
        self.poll_interval_s = poll_interval_s
        self.spider_depth = spider_depth
        self.max_pages = max_pages
        self.progress_cb = progress_cb or (lambda pct: None)
        self.deadline = time.monotonic() + scan_budget_s
        self._session = self._make_session()

    # -- plumbing ---------------------------------------------------------

    def _make_session(self):
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        session = requests.Session()
        retry = Retry(
            total=3,
            connect=3,
            read=2,
            backoff_factor=0.5,
            status_forcelist=(500, 502, 503, 504),
            allowed_methods=frozenset(),  # retry any method (all calls are GETs)
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _get(self, path: str, params: dict | None = None):
        params = dict(params or {})
        if self.api_key:
            params["apikey"] = self.api_key
        resp = self._session.get(
            self.base + path, params=params, timeout=self.request_timeout
        )
        resp.raise_for_status()
        return resp.json()

    def _report(self, pct: float) -> None:
        try:
            self.progress_cb(max(0, min(100, int(pct))))
        except Exception:  # progress reporting must never fail the scan
            pass

    def _check_deadline(self, phase: str) -> None:
        if time.monotonic() > self.deadline:
            raise RuntimeError(
                f"ZAP scan budget of {self.scan_budget_s}s exceeded "
                f"during {phase}."
            )

    # -- ZAP API surface ---------------------------------------------------

    def version(self) -> str:
        return str(self._get("/JSON/core/view/version/").get("version", ""))

    def new_session(self) -> None:
        """Fresh ZAP session so scans stay isolated from each other."""
        self._get("/JSON/core/action/newSession/", {"overwrite": "true"})

    def set_auth_header(self, name: str, value: str) -> bool:
        """Register a request header via the Replacer add-on (best effort).

        Returns False (scan continues unauthenticated) when the add-on is
        missing or rejects the rule.
        """
        try:
            data = self._get(
                "/JSON/replacer/action/add/",
                {
                    "description": self.AUTH_RULE_DESCRIPTION,
                    "enabled": "true",
                    "matchtype": "REQ_HEADER",
                    "match": name,
                    "replacement": value,
                },
            )
        except Exception:
            return False
        return not (isinstance(data, dict) and ("error" in data or "code" in data))

    def clear_auth_header(self) -> None:
        try:
            self._get(
                "/JSON/replacer/action/remove/",
                {"description": self.AUTH_RULE_DESCRIPTION},
            )
        except Exception:
            pass

    def _access_target(self) -> None:
        self._get("/JSON/core/action/accessUrl/", {"url": self.target_url})

    def spider(self) -> list[str]:
        params = {"url": self.target_url, "recurse": "true"}
        if self.spider_depth is not None:
            params["maxDepth"] = str(self.spider_depth)
        if self.max_pages is not None:
            params["maxChildren"] = str(self.max_pages)
        data = self._get("/JSON/spider/action/scan/", params)
        scan_id = str(data.get("scan", "0"))
        while True:
            self._check_deadline("spider")
            status = str(
                self._get("/JSON/spider/view/status/", {"scanId": scan_id})
                .get("status", "0")
            )
            pct = int(float(status or 0))
            self._report(12 + pct * 0.28)  # spider owns 12%..40%
            if pct >= 100:
                break
            time.sleep(self.poll_interval_s)
        results = self._get(
            "/JSON/spider/view/results/", {"scanId": scan_id}
        ).get("results", [])
        return [str(u) for u in results]

    def _wait_passive(self, lo: float, hi: float) -> None:
        """Wait until the passive scanner drains its queue."""
        while True:
            self._check_deadline("passive scan")
            remaining = self._records_to_scan()
            self._report(hi if remaining == 0 else (lo + hi) / 2)
            if remaining == 0:
                return
            time.sleep(self.poll_interval_s)

    def _records_to_scan(self) -> int:
        import requests

        # ZAP >= 2.17 serves this view from the pscan add-on; older builds
        # from core. If neither exists, don't block the scan on it.
        for path in (
            "/JSON/pscan/view/recordsToScan/",
            "/JSON/core/view/recordsToScan/",
        ):
            try:
                raw = self._get(path).get("recordsToScan", "0") or 0
                return int(float(raw))
            except requests.HTTPError:
                continue
        return 0

    def active_scan(self) -> None:
        data = self._get(
            "/JSON/ascan/action/scan/",
            {"url": self.target_url, "recurse": "true"},
        )
        scan_id = str(data.get("scan", "0"))
        while True:
            self._check_deadline("active scan")
            status = str(
                self._get("/JSON/ascan/view/status/", {"scanId": scan_id})
                .get("status", "0")
            )
            pct = int(float(status or 0))
            self._report(50 + pct * 0.4)  # active scan owns 50%..90%
            if pct >= 100:
                break
            time.sleep(self.poll_interval_s)

    def alerts(self, count: int = 1000) -> list[dict]:
        out: list[dict] = []
        start = 0
        while True:
            data = self._get(
                "/JSON/core/view/alerts/",
                {
                    "baseurl": self.target_url,
                    "start": str(start),
                    "count": str(count),
                },
            )
            batch = data.get("alerts", [])
            out.extend(batch)
            if len(batch) < count:
                return out
            start += count

    # -- orchestration -----------------------------------------------------

    def execute(self) -> list[dict]:
        """Run the configured scan type; return mapped finding dicts."""
        self._check_deadline("startup")
        self._report(10)
        self.new_session()
        self._access_target()
        if self.scan_type == "baseline":
            self._wait_passive(12, 88)
        elif self.scan_type == "spider":
            self.spider()
            self._wait_passive(40, 88)
        else:  # active | full
            self.spider()
            self._wait_passive(40, 48)
            self.active_scan()
        self._report(92)
        return [map_alert(a) for a in self.alerts()]


# Backwards-compatible alias (the old stub class shared this name).
ZapClient = RealZapClient
