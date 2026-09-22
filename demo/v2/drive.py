"""Drive the SecureScan demo end-to-end, recording real frames via CDP screencast."""
import sys
import time

sys.path.insert(0, "/home/alaqmar/pentest001/challenge/demo/v2")
from cdp import Page  # noqa: E402

BASE = "http://127.0.0.1:8472"
REPO = "https://github.com/Alaqmar-morawala/securescan-kiro-university"
LESSONS = "https://kiro.dev/2026/university/"
OUT = "/home/alaqmar/pentest001/challenge/demo/v2/frames"

p = Page()
p.start_recording()
p.pump(1.0)


def hold(secs):
    p.pump(secs)


print("=== 1. landing ===")
p.goto(BASE, settle=2.5)
p.banner("SecureScan — Kiro University Challenge 2026 (final exam project)", 2.2)
p.highlight("a.btn-primary", "#22c55e"); hold(1.4)
p.clear_highlights()

print("=== 2. register ===")
p.goto(BASE + "/accounts/register/", settle=1.8)
p.banner("Register a user (Django auth)", 1.6)
p.type_into("input[name=username]", "demo-user")
p.type_into("input[name=password1]", "StrongPass!234")
p.type_into("input[name=password2]", "StrongPass!234")
p.highlight("button", "#22c55e"); hold(1.0)
p.click_text("Create account", tag="button", settle=2.2)
p.banner("Dashboard", 1.6)
hold(1.4)

print("=== 3. add target ===")
p.goto(BASE + "/targets/add/", settle=1.6)
p.banner("Add a website you own — URL allowlist (http/https only)", 1.8)
p.type_into("input[name=name]", "my-demo-site")
p.type_into("input[name=url]", "https://example.com")
p.highlight("button", "#22c55e"); hold(1.0)
p.click_text("Save", tag="button", settle=2.2)

print("=== 4. configure scan + cost estimate ===")
p.banner("Configure scan: type, depth, pages → instant cost estimate", 1.8)
hold(1.0)
p.set_select("select[name=scan_type]", "full"); hold(0.7)
p.type_into("input[name=spider_depth]", "3")
p.type_into("input[name=max_pages]", "60")
p.highlight("form", "#f59e0b"); hold(1.2)
p.click_text("Estimate", tag="button", settle=2.2)

print("=== 5. scan detail + start ===")
p.banner("Scan created — QUEUED (isolated container per scan)", 1.8)
p.highlight("p", "#38bdf8"); hold(1.6)
p.clear_highlights()
p.click_text("Start scan", tag="button", settle=3.0)
p.banner("Scan DONE — 5 severity-classified findings", 2.0)
p.highlight("table", "#22c55e"); hold(2.6)
p.clear_highlights()

print("=== 6. HTML report + PDF ===")
sid = p.js("document.querySelector('a[href$=\"report.html\"]').getAttribute('href').split('/')[2]")
print("scan id:", sid)
p.goto(f"{BASE}/scans/{sid}/report.html", settle=1.8)
p.banner("HTML report — severity-ordered (High > Medium > Low > Info)", 2.0)
p.highlight("table", "#22c55e"); hold(2.4)
p.clear_highlights()
p.click_text("Download PDF", tag="a", settle=2.6)
p.banner("PDF exported (reportlab)", 1.8)
hold(1.8)

print("=== 7. history ===")
p.goto(BASE + "/history/", settle=1.6)
p.banner("Scan history — newest first, owner-isolated", 1.8)
p.highlight("table", "#38bdf8"); hold(2.2)

print("=== 8. .kiro evidence on GitHub ===")
p.goto(REPO, settle=3.5)
p.banner("Public repo with full .kiro evidence", 2.2)
hold(2.6)
p.goto(REPO + "/tree/main/securescan/.kiro", settle=3.5)
p.banner("Lessons 1-3: specs + steering + hooks", 2.0)
hold(2.6)
p.goto(REPO + "/tree/main/securescan/powers/secscan-django", settle=3.5)
p.banner("Lesson 5 + Bonus 2: a Kiro power created for this project", 2.0)
hold(2.6)
p.goto(REPO + "/tree/main/securescan/.kiro/agents", settle=3.5)
p.banner("Lesson 7: custom agents", 1.8)
hold(2.4)
p.goto(REPO + "/commits/main", settle=3.5)
p.banner("Lesson-driven, incremental commits during the challenge", 2.0)
hold(2.6)

print("=== 10. tests (green) ===")
p.goto("file:///home/alaqmar/pentest001/challenge/demo/v2/tests.html", settle=1.8)
p.banner("Verification: 9/9 tests green (5 example + 4 property-based)", 2.2)
hold(3.2)
p.banner("Thanks for watching — SecureScan, built with Kiro", 2.2)
hold(2.0)

n, dur = p.stop_and_write(OUT)
print(f"frames={n} duration={dur:.1f}s")
