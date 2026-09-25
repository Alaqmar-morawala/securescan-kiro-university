"""One-shot demo: run a REAL ZAP scan through the full Django stack.

Starts the bundled vulnerable demo target on an ephemeral loopback port,
forces the real engine (SECURESCAN_MOCK=0), executes run_scan() exactly as
the app would, then saves the generated PDF/CSV report and a findings list
under demo/real-scan/ as submission evidence.

Usage:  python manage.py shell < demo_real_scan.py   (or run via bash below)
"""

import csv
import io
import os
import threading

os.environ["SECURESCAN_MOCK"] = "0"
os.environ["SECURESCAN_ALLOW_PRIVATE_TARGETS"] = "1"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402

settings.SECURESCAN_MOCK = False  # belt & braces: the real engine

from django.contrib.auth.models import User  # noqa: E402

from reports.services import (  # noqa: E402
    build_pdf_bytes,
    ordered_findings,
    severity_summary,
)
from scanner.docker_runner import run_scan, seed_estimate  # noqa: E402
from scanner.engine import resolve_engine  # noqa: E402
from scanner.management.commands.vuln_target import make_server  # noqa: E402
from scanner.models import Scan, ScanConfig, Target  # noqa: E402
from scanner import zap_process  # noqa: E402

ZAP_HOST = settings.SECURESCAN_ZAP_HOST
ZAP_PORT = settings.SECURESCAN_ZAP_PORT

if not zap_process.zap_ready(ZAP_HOST, ZAP_PORT):
    print("starting ZAP daemon ...")
    zap_process.start_daemon(ZAP_HOST, ZAP_PORT, settings.SECURESCAN_ZAP_API_KEY)

httpd = make_server("127.0.0.1", 0)
threading.Thread(target=httpd.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{httpd.server_address[1]}/"
print("vulnerable target:", url)

plan = resolve_engine()
print("engine:", plan.mode, "-", plan.reason)
assert plan.is_real

user, _ = User.objects.get_or_create(username="real-e2e")
target = Target.objects.create(
    owner=user,
    name=f"Vulnerable demo app ({os.getpid()})",
    url=url,
)
config = ScanConfig.objects.create(
    target=target, scan_type="full", spider_depth=2, max_pages=25
)
scan = Scan.objects.create(owner=user, target=target, config=config)
seed_estimate(scan)
run_scan(scan)
scan.refresh_from_db()
print("status:", scan.status, "| error:", scan.error[:200])
assert scan.status == "DONE", scan.error

findings = ordered_findings(scan)
summary = severity_summary(findings)
print(f"\nREAL FINDINGS ({summary['total']}, overall: {summary['overall']}):")
for f in findings:
    print(f"  [{f.severity:6}] {f.name}  ({f.cwe or '-'})")

os.makedirs("../demo/real-scan", exist_ok=True)
with open("../demo/real-scan/report.pdf", "wb") as fh:
    fh.write(build_pdf_bytes(scan))
buf = io.StringIO()
writer = csv.writer(buf)
writer.writerow(["Severity", "Finding", "URL", "CWE", "Description", "Solution"])
for f in findings:
    writer.writerow([f.severity, f.name, f.url, f.cwe, f.description, f.solution])
with open("../demo/real-scan/report.csv", "w") as fh:
    fh.write(buf.getvalue())
zap_version = zap_process.zap_ready(ZAP_HOST, ZAP_PORT)
with open("../demo/real-scan/findings.txt", "w") as fh:
    fh.write(
        "Real OWASP ZAP scan executed by SecureScan's real engine "
        "(run_scan, SECURESCAN_MOCK=0)\n"
        f"Target: {url} (bundled 'vuln_target' demo app)\n"
        f"Scan type: {scan.config.scan_type}, spider depth "
        f"{scan.config.spider_depth}, max pages {scan.config.max_pages}\n\n"
        + "\n".join(
            f"[{f.severity}] {f.name} ({f.cwe})" for f in findings
        )
        + "\n"
    )
print("\nsaved: demo/real-scan/{report.pdf,report.csv,findings.txt}")
httpd.shutdown()
httpd.server_close()
