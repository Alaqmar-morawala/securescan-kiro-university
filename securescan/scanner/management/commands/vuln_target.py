"""Run the bundled deliberately-vulnerable demo target.

A tiny stdlib-only web app with realistic, easily-detected weaknesses so
the real ZAP engine has something true to find:

* reflected XSS — ``/search?q=<input>`` echoed without encoding
* error-based SQLi signature — ``/user?id=1'`` returns a MySQL-style error
* missing security headers — no CSP / X-Content-Type-Options /
  X-Frame-Options / HSTS anywhere
* insecure cookie — ``/login`` sets ``sessionid`` without
  Secure/HttpOnly/SameSite
* verbose banner — ``Server: InsecureDemo/1.0 Python/<ver>``

Usage:
    python manage.py vuln_target --port 8473
Point SecureScan at http://127.0.0.1:<port>/ with
SECURESCAN_ALLOW_PRIVATE_TARGETS=1 (local demos/tests ONLY).
"""

import threading
from http.server import ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from django.core.management.base import BaseCommand

_PAGE = """<!doctype html>
<html><head><title>Insecure demo app</title></head>
<body>
<h1>Insecure demo app</h1>
<ul>
  <li><a href="/search?q=hello">/search</a> — reflects your query</li>
  <li><a href="/user?id=1">/user</a> — profile lookup</li>
  <li><a href="/login">/login</a> — sets a session cookie</li>
</ul>
</body></html>"""


class VulnerableHandler:
    """Mixin providing the insecure responses; combined with the stdlib
    request handler class in :func:`make_server`."""

    server_version = "InsecureDemo/1.0"
    protocol_version = "HTTP/1.1"

    def _respond(self, code, body, extra_headers=None):
        payload = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        # Deliberately NO CSP / X-Content-Type-Options / X-Frame-Options /
        # HSTS / Referrer-Policy — passive ZAP rules flag all of these.
        for key, value in (extra_headers or []):
            self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(payload)

    def do_GET(self):
        try:
            parts = urlsplit(self.path)
            qs = parse_qs(parts.query)
            if parts.path in ("", "/"):
                self._respond(200, _PAGE)
            elif parts.path == "/search":
                query = (qs.get("q", [""])[0])[:200]
                # Deliberately unencoded reflection (reflected XSS).
                self._respond(
                    200,
                    f"<html><body>Results for: {query}"
                    "<!-- search end --></body></html>",
                )
            elif parts.path == "/user":
                user_id = (qs.get("id", [""])[0])[:100]
                if "'" in user_id:
                    # Deliberately verbose DB error (error-based SQLi hint).
                    self._respond(
                        500,
                        "<html><body>Database error: You have an error in "
                        "your SQL syntax near '" + user_id + "' in statement "
                        "SELECT * FROM users WHERE id=" + user_id + "</body>"
                        "</html>",
                    )
                else:
                    self._respond(
                        200,
                        f"<html><body>User {user_id}: demo@example.test"
                        "</body></html>",
                    )
            elif parts.path == "/login":
                # Deliberately missing Secure / HttpOnly / SameSite.
                self._respond(
                    200,
                    "<html><body>Logged in as demo</body></html>",
                    extra_headers=[
                        ("Set-Cookie", "sessionid=demo-session-123; Path=/"),
                    ],
                )
            else:
                self._respond(404, "<html><body>Not found</body></html>")
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception:
            try:
                self._respond(500, "<html><body>Oops</body></html>")
            except Exception:
                pass

    def do_HEAD(self):
        self.do_GET()

    def do_POST(self):
        self._respond(200, "<html><body>OK</body></html>")


def make_server(bind: str, port: int):
    """Build (not start) a ThreadingHTTPServer serving the vulnerable app."""
    import http.server

    handler = type(
        "BoundVulnerableHandler",
        (VulnerableHandler, http.server.BaseHTTPRequestHandler),
        {},
    )
    return ThreadingHTTPServer((bind, port), handler)


class Command(BaseCommand):
    help = "Run the bundled deliberately-vulnerable demo target."

    def add_arguments(self, parser):
        parser.add_argument("--port", type=int, default=8473)
        parser.add_argument("--bind", default="127.0.0.1")

    def handle(self, *args, **options):
        bind = options["bind"]
        port = options["port"]
        httpd = make_server(bind, port)
        self.stdout.write(
            self.style.SUCCESS(
                f"Vulnerable demo target on http://{bind}:{port}/ "
                "(Ctrl+C to stop)"
            )
        )
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            httpd.shutdown()
            httpd.server_close()
