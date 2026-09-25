"""Drive the REAL-engine demo: register -> scan the bundled vulnerable app
with a live OWASP ZAP daemon -> real severity-ordered findings -> reports
-> .kiro lesson tour. Frames captured via CDP screencast.

The ~110s real scan is recorded faithfully, then its slice of the frames
timeline is compressed (time-lapse) so the whole video fits the 3-minute
final-exam cap while the progress bar motion stays visible.
"""
import sys
import time

sys.path.insert(0, "/home/alaqmar/pentest001/challenge/demo/v2")
from cdp import Page  # noqa: E402

BASE = "http://127.0.0.1:8472"
REPO = "https://github.com/Alaqmar-morawala/securescan-kiro-university"
OUT = "/home/alaqmar/pentest001/challenge/demo/v2/frames"
LAPSE = 0.3  # timeline compression factor for the scan segment

p = Page()
p.start_recording()
p.pump(0.8)

print("=== 1. landing (Live ZAP engine chip) ===")
p.goto(BASE, settle=2.0)
p.banner("SecureScan — real OWASP ZAP engine · Kiro University Challenge 2026", 2.2)
p.highlight(".engine-chip", "#22c55e")
p.banner("Header chip: LIVE ZAP engine detected — deterministic demo fixtures as offline fallback", 1.8)
p.clear_highlights()

print("=== 2. register ===")
p.goto(BASE + "/accounts/register/", settle=1.4)
p.banner("Register a user (Django auth)", 1.2)
p.type_into("input[name=username]", "real-demo")
p.type_into("input[name=password1]", "StrongPass!234")
p.type_into("input[name=password2]", "StrongPass!234")
p.click_text("Create account", tag="button", settle=1.8)
p.banner("Dashboard — engine status visible on every page", 1.2)

print("=== 3. add the bundled vulnerable app as target ===")
p.goto(BASE + "/targets/add/", settle=1.4)
p.banner("Target: bundled deliberately-vulnerable demo app (manage.py vuln_target)", 1.6)
p.type_into("input[name=name]", "vuln-demo-app")
p.type_into("input[name=url]", "http://127.0.0.1:8473/")
p.banner("SSRF guard: private targets need SECURESCAN_ALLOW_PRIVATE_TARGETS=1 (local demos only)", 1.4)
p.click_text("Save", tag="button", settle=1.8)

print("=== 4. configure + estimate ===")
p.banner("Configure scan: type, depth, page budget — cost + duration estimate up front", 1.4)
p.set_select("select[name=scan_type]", "full")
p.type_into("input[name=spider_depth]", "2")
p.type_into("input[name=max_pages]", "25")
p.click_text("Estimate", tag="button", settle=2.0)

print("=== 5. start REAL scan ===")
p.banner("Start scan → real ZAP: session reset, spider, passive drain, ACTIVE scan", 1.8)
t_scan_start = time.time()
p.click_text("Start scan", tag="button", settle=3.0)

deadline = time.time() + 145
phase = ""
while time.time() < deadline:
    pct = p.js("(function(){var l=document.querySelector('[data-progress-label]');return l?parseInt(l.textContent)||0:-1})()", 0.05)
    if pct is None or pct < 0:
        p.pump(1.0)
        continue
    if pct < 40 and phase != "spider":
        phase = "spider"
        p.banner(f"Real ZAP: spidering the target within the depth budget… ({pct}%)", 0.6)
    elif 40 <= pct < 50 and phase != "passive":
        phase = "passive"
        p.banner("Real ZAP: passive rules draining the queue…", 0.6)
    elif pct >= 50 and phase != "active":
        phase = "active"
        p.banner(f"Real ZAP: ACTIVE scan — injection rules attacking every parameter ({pct}%)", 0.6)
    elif pct >= 95 and phase != "alerts" and pct < 100:
        phase = "alerts"
        p.banner("Real ZAP: collecting alerts from the scan session…", 0.6)
    if pct >= 100:
        break
    p.pump(1.0)

t_scan_end = time.time()
print(f"scan wall time: {t_scan_end - t_scan_start:.0f}s")

p.banner("Scan DONE — real alerts from OWASP ZAP 2.17", 1.4, "#22c55e")
p.highlight("table", "#22c55e")
p.banner("Real findings, severity-ordered: High XSS (CWE-79) + SQLi (CWE-89) discovered by ZAP", 2.2, "#22c55e")
p.clear_highlights()

print("=== 6. reports ===")
p.click_text("HTML report", tag="a", settle=1.6)
p.banner("HTML report — every finding with description + fix guidance", 1.6)
p.click_text("Download PDF", tag="a", settle=2.0)
p.banner("PDF + CSV exports (reportlab, executive summary included)", 1.6)

print("=== 7. .kiro lesson tour (each required lesson) ===")
p.goto(REPO + "/tree/main/securescan/.kiro", settle=3.0)
p.banner("L1 specs · L2 steering · L3 hooks — the .kiro folder ships in the public repo", 2.2)
p.goto(REPO + "/blob/main/securescan/tests/test_properties_cost.py", settle=3.0)
p.banner("L4 property-based testing — hypothesis, 100+ examples per property", 2.2)
p.goto(REPO + "/tree/main/securescan/powers/secscan-django", settle=3.0)
p.banner("L5 power (install+use) · L6 MCP servers — powers/secscan-django + mcp.json", 2.2)
p.goto(REPO + "/tree/main/securescan/.kiro/agents", settle=3.0)
p.banner("L7 custom agents — securescan-reviewer + zap-operator", 2.2)

print("=== 8. tests + outro ===")
p.goto("file:///home/alaqmar/pentest001/challenge/demo/v2/tests.html", settle=1.6)
p.banner("65/65 offline tests green + opt-in live ZAP integration test", 2.0)
p.banner("Built with Kiro — SecureScan scans apps for real", 1.8)
p.pump(1.0)

n, dur = p.stop_and_write(OUT)
print(f"frames={n} wall={dur:.1f}s")

# ---- time-lapse the scan segment in frames.txt (honest demo pacing) ----
def compress():
    scaled = 0
    with open(f"{OUT}/frames.txt") as fh:
        lines = fh.read().splitlines()
    out = []
    for i, line in enumerate(lines):
        if line.startswith("duration ") and i >= 1:
            idx = int(lines[i - 1].split("'")[1][1:-4])
            if idx < len(p.frames):
                ts = p.frames[idx][0]
                if t_scan_start <= ts <= t_scan_end:
                    d = float(line.split()[1]) * LAPSE
                    line = f"duration {max(d, 1/30.0):.3f}"
                    scaled += 1
        out.append(line)
    with open(f"{OUT}/frames.txt", "w") as fh:
        fh.write("\n".join(out) + "\n")
    print(f"compressed {scaled} frame durations by {LAPSE}")

compress()
