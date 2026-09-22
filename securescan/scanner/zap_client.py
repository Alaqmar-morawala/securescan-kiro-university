"""OWASP ZAP client: real REST stub + deterministic mock for dev/tests/demo."""

from __future__ import annotations

import requests


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
        findings = [dict(f, url=f["url"].replace("https://target.example", self.target_url.rstrip("/"))) for f in MOCK_FINDINGS]
        if self.scan_type == "baseline":
            return [f for f in findings if f["severity"] in ("High", "Medium")]
        return findings


class ZapClient:
    """Thin wrapper over ZAP REST API (used when SECURESCAN_MOCK=0 + real ZAP)."""

    def __init__(self, zap_base: str, api_key: str = ""):
        self.base = zap_base.rstrip("/")
        self.api_key = api_key

    def _get(self, path: str, params: dict | None = None):
        params = dict(params or {})
        if self.api_key:
            params["apikey"] = self.api_key
        resp = requests.get(self.base + path, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def spider(self, target_url: str) -> list[str]:
        data = self._get("/JSON/spider/action/scan/", {"url": target_url})
        _ = data  # scan id ignored in this minimal client
        return [target_url]

    def alerts(self, target_url: str) -> list[dict]:
        data = self._get("/JSON/core/view/alerts/", {"baseurl": target_url})
        return data.get("alerts", [])
