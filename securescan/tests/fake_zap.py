"""In-process fake ZAP REST API for testing RealZapClient without a daemon.

Implements just enough of the ZAP API surface (version, session, spider,
passive drain, active scan, alerts, replacer) with deterministic state
transitions, plus fault injection (a one-shot 502) for retry tests.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

ALERTS = [
    {
        # ZAP 2.17-style string risk names, as returned by a real daemon.
        "alert": "Cross Site Scripting (Reflected)",
        "risk": "High",
        "confidence": "Medium",
        "url": "http://target.example/search?q=",
        "description": "desc-xss",
        "solution": "fix-xss",
        "cweid": "79",
        "pluginid": "40012",
    },
    {
        # Numeric risk, as returned by older ZAP builds (backwards compat).
        "alert": "X-Content-Type-Options Header Missing",
        "risk": "1",
        "confidence": "3",
        "url": "http://target.example/",
        "description": "desc-xcto",
        "solution": "fix-xcto",
        "cweid": "16",
        "pluginid": "10038",
    },
    {
        "alert": "Info Leak",
        "risk": "Informational",
        "confidence": "2",
        "url": "http://target.example/",
        "description": "desc-info",
        "solution": "fix-info",
        "cweid": "",
        "pluginid": "100",
    },
]


class FakeZap:
    """Stateful route handler; one instance per test server."""

    def __init__(self, *, api_key: str = "", fail_version_once: bool = False):
        self.api_key = api_key
        self.fail_version_once = fail_version_once
        self.requests: list[tuple[str, dict]] = []
        self.auth_rules: list[dict] = []
        self.removed_rules: list[dict] = []
        self._spider_polls = 0
        self._ascan_polls = 0
        self._version_fails = 0

    # -- route dispatch -----------------------------------------------------

    def route(self, path: str, qs: dict) -> tuple[int, dict]:
        self.requests.append((path, qs))
        if self.api_key and qs.get("apikey") != self.api_key:
            return 403, {"code": "forbidden", "message": "api key required"}

        if path == "/JSON/core/view/version/":
            if self.fail_version_once and self._version_fails == 0:
                self._version_fails += 1
                return 502, {"error": "boom"}
            return 200, {"version": "2.17.0-fake"}
        if path == "/JSON/core/action/newSession/":
            return 200, {"result": "OK"}
        if path == "/JSON/core/action/accessUrl/":
            return 200, {"result": "OK"}
        if path == "/JSON/core/view/recordsToScan/":
            return 200, {"recordsToScan": "0"}
        if path == "/JSON/core/view/alerts/":
            start = int(qs.get("start", "0"))
            count = int(qs.get("count", "1000"))
            return 200, {"alerts": ALERTS[start:start + count]}
        if path == "/JSON/spider/action/scan/":
            return 200, {"scan": "0"}
        if path == "/JSON/spider/view/status/":
            self._spider_polls += 1
            return 200, {"status": str(min(100, 50 * self._spider_polls))}
        if path == "/JSON/spider/view/results/":
            return 200, {
                "results": [
                    "http://target.example/",
                    "http://target.example/about",
                ]
            }
        if path == "/JSON/ascan/action/scan/":
            return 200, {"scan": "0"}
        if path == "/JSON/ascan/view/status/":
            self._ascan_polls += 1
            return 200, {"status": str(min(100, 40 * self._ascan_polls))}
        if path == "/JSON/replacer/action/add/":
            self.auth_rules.append(qs)
            return 200, {"result": "OK Added replacer rule."}
        if path == "/JSON/replacer/action/remove/":
            self.removed_rules.append(qs)
            return 200, {"result": "OK Removed"}
        return 404, {"error": f"no route {path}"}


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self):  # noqa: N802 - stdlib signature
        parts = urlsplit(self.path)
        qs = {k: v[0] for k, v in parse_qs(parts.query).items()}
        status, payload = self.server.fake.route(parts.path, qs)
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # silence test output
        pass


class FakeZapServer:
    """Threaded localhost server wrapping a FakeZap."""

    def __init__(self, fake: FakeZap):
        self.fake = fake
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        self.httpd.fake = fake
        self.port = self.httpd.server_address[1]
        self._thread = threading.Thread(
            target=self.httpd.serve_forever, daemon=True
        )

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self.httpd.shutdown()
        self.httpd.server_close()
        return False
