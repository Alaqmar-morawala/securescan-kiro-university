# HANDOFF — SecureScan / Kiro University Challenge 2026

> Read this file first. Single source of truth for any agent continuing here.
> Verify claims against listed paths before changing anything.
> Do NOT commit after the freeze date (§6.2).

## 1. Mission & current state

- **Goal:** Win Kiro University Challenge 2026 Final Exam credits with the
  SecureScan Django app (also the owner's Parul University SE-lab project).
- **Status (2026-09-25): BUILD COMPLETE + REAL ENGINE, SUBMISSION PENDING.**
  App works end-to-end, 65/65 offline tests pass (+ opt-in live ZAP test), repo
  public + pushed, real 2m15s demo video public. The OWASP ZAP path is now real
  (§10): full client, daemon lifecycle, SSRF guard, evidence in `demo/real-scan/`.
  Two human-only actions remain (social post + entry form).
- **Expected award on free plan: 5,000 credits**
  (7 lessons + completion + Bonus 2; Bonus 1 cloud is paid-only, not claimed).

## 2. Key links & locations

| Item | Value |
|---|---|
| Local repo root | `/home/alaqmar/pentest001/challenge` (git; app in `securescan/`) |
| Public GitHub | `https://github.com/Alaqmar-morawala/securescan-kiro-university` (`main`) |
| Demo video (real E2E, ~2m15s) | `https://github.com/Alaqmar-morawala/securescan-kiro-university/releases/download/final-demo/securescan-demo-real.mp4` (release `final-demo`; local `demo/v2/securescan-demo-real.mp4`) |
| Challenge page | `https://kiro.dev/2026/university/` |
| Terms (binding) | `https://kiro.dev/2026/university/terms/` |
| Entry form | Opens **Fri Sep 25** at challenge page, due **Mon Oct 5, 23:59 PT** |
| Submission checklist | `SUBMIT.md` (social-post draft + form writeup + freeze warning) |
| Lesson evidence map | `securescan/README.md` |
| Cloud bonus status | `securescan/CLOUD.md` (NOT claimed — free plan) |
| Raw lesson extracts | `/tmp/lessons/*-FULL.txt` (scraping artifacts, not in git) |
| Uni assignment source | `/home/alaqmar/pentest001/Merged_20260731_0741.pdf` (Parul SE Practicals 1–4) |

## 3. Environment & accounts

- Linux, Python 3.14.7, Django 5.2.17, hypothesis 6.168.0, reportlab 5.0.0,
  pytest 9.1.1 + pytest-django 4.14.0.
- `kiro-cli 2.20.1` at `/home/alaqmar/.local/bin/kiro-cli`, Builder ID
  `2403051050600@paruluniversity.ac.in`, **free plan**. `doctor` terminal warnings
  are pre-existing noise — ignore.
- GitHub via `gh`: active `Alaqmar-morawala` (created 2025-09-15, >3mo ✓).
  Inactive `saif-pvt` also authed — **never use it** (one GitHub account per entrant).
- Git identity: `Alaqmar-morawala <2403051050600@paruluniversity.ac.in>`.
- Docker 28.5.2 present but **not required** (mock mode).

## 4. Repo map (relative to `/home/alaqmar/pentest001/challenge/`)

- `README.md` — repo pointer; `SUBMIT.md` — human checklist (keep updated).
- `securescan/` — Django root (`manage.py` here):
  - `config/settings.py` — `SECURESCAN_MOCK=True`; `ALLOWED_HOSTS` incl. `testserver`.
  - `accounts/` — register/login/logout/dashboard (`views.py`, `urls.py`).
  - `scanner/` — `Target/ScanConfig/Scan/Finding` models; `forms.py`;
    `services.py` (`estimate_cost`, `order_findings`); `zap_client.py` (Mock + real);
    `docker_runner.py` (`run_scan`, finally-cleanup); `views.py`, `urls.py`.
  - `reports/` — `services.build_pdf_bytes` (reportlab); HTML+PDF views/urls.
  - `templates/` — base, landing, dashboard, accounts/*, scanner/*, reports/report.html.
  - `tests/` — `conftest.py` (django.setup), `test_example.py` (5), `test_properties_*`.
  - `pytest.ini` — `DJANGO_SETTINGS_MODULE=config.settings`.
  - `.kiro/specs/securescan/{requirements,design,tasks}.md` — L1.
  - `.kiro/steering/{product,tech,testing}.md` — L2.
  - `.kiro/hooks/python-checks.json` — L3.
  - `.kiro/settings/mcp.json` — L6 (fetch).
  - `.kiro/agents/{securescan-reviewer,zap-operator}.json` — L7.
  - `powers/secscan-django/{plugin.json,mcp.json,skills/scan-patterns/{SKILL.md,references/severity.md}}` — L5 + Bonus 2.
  - `ARCHITECTURE.md`, `CLOUD.md`, `README.md`.
- `demo/` — committed mp4, PDFs, screenshots, `scan_id.txt`.
- Git: `ac42d1c` → `9e81ca0` → `2d8fd75`, `origin/main` pushed clean.


## 5. How to verify (all must pass)

```bash
cd /home/alaqmar/pentest001/challenge/securescan
python3 -m pytest tests/ -q -p no:cacheprovider   # expect: 65 passed, 1 skipped
RUN_ZAP_E2E=1 python3 -m pytest tests/test_real_zap_integration.py -q  # optional: real ZAP scan (needs zaproxy)
python3 manage.py check                            # expect: no issues
python3 manage.py migrate && python3 manage.py runserver 127.0.0.1:8472
# register → /targets/add/ (https://example.com) → configure (full, depth 3,
# 60 pages) → Start scan → DONE, 5 findings → /report.html + /report.pdf → /history/
rm -f db.sqlite3   # IMPORTANT: never commit db.sqlite3 (gitignored)
```

## 6. Binding rules (from /terms, verified 2026-09-22)

1. First commit ≥ **Sep 21, 09:00 PT**, none earlier — satisfied (born Sep 22).
2. **COMMIT FREEZE: no commits Oct 5 23:59 PT → judging end (~Oct 19) or award
   email.** No commit/push in that window.
3. Public repo + `.kiro/` lesson content — present (§4).
4. Kiro as primary dev tool — true (kiro-cli build).
5. Working project, not mockup — CRUD + scan run + PDF (mock fixtures only replace
   external ZAP/Docker; judged path).
6. Demo video 30s–3min, project + each lesson — 72s release ✓.
7. Public X/LinkedIn post: repo link + 2–3 sentence description +
   `#KiroUniversity #BuildWithKiro` + tag `@kirodotdev`/`@kiro` + public video —
   **TODO (human)**.
8. Entry form (from Sep 25): repo + video + post links, description, per-lesson
   writeup, correct email, by Oct 5 23:59 PT — **TODO (human)**.
9. One entry/person; individual work; GitHub (3mo+) matches one social account.
10. Bonus 1 cloud = paid only (not claimed). Bonus 2 create-a-power = claimed via
    `powers/secscan-django/`. Neither affects the +1000 completion award.

## 7. What remains (ordered)

- [ ] **Human:** publish social post (draft in `SUBMIT.md`).
- [ ] **Human (from Sep 25):** submit entry form (writeup in `SUBMIT.md` + evidence
      map in `securescan/README.md`); double-check contact email.
- [ ] **Any agent (before Oct 5 ONLY):** fix reported bugs; re-run §5; re-record
      video ONLY if behavior changed; keep commits minimal.
- [ ] **After Oct 5 23:59 PT:** hands off keyboards — no commits until cleared.
- [ ] Optional (paid upgrade before Oct 5): cloud session + config sync per
      `securescan/CLOUD.md` to claim Bonus 1 (+250). Do NOT attempt on free plan.

## 8. Gotchas for next agent

- Playwright (system pkg) is broken here (`Connection closed`); Chromium headless
  `--screenshot` works — use it, don't debug Playwright.
- `db.sqlite3` regenerates on migrate/runserver; delete before committing.
- `__pycache__/` is gitignored; if `git status` shows it, `git rm -r --cached` it.
- Tests need `pytest.ini` + `tests/conftest.py` (`django.setup()`); DB tests use
  `pytest-django`. Don't remove these. Keep `testserver` in `ALLOWED_HOSTS`.
- `RegisterView` redirects to literal `/accounts/` (no `dashboard` URL name) —
  intentional, don't "fix".
- Detail template lists findings in insertion order; P2 ordering is enforced in
  `order_findings()` + report builder — don't touch without checking P2 tests.
- Real-Docker path in `docker_runner` intentionally errors when unconfigured; mock
  path is the judged path. Keep `SECURESCAN_MOCK=True`.
  (UPDATED 2026-09-25: the real path is now fully implemented — see §10. Mock
  remains the Vercel/judged mode; tests force mock in `tests/conftest.py`, which
  also must run AFTER pytest-django imports settings — keep that ordering.)
- `securescan/README.md` references `docs/SPRINTS.md` + `docs/SPMP.md` for the uni
  mapping — both exist since commit 5207025 (older copies of this note said
  "never created"; that was stale).
- Demo screenshots rendered from saved HTML via `file://` (Bootstrap CDN unstyled
  offline) — evidence only; re-record properly if needed.

## 9. Prior-turn context (why things are this way)

- Owner asked to earn "the whole 5.25k" on kiro-cli free, reusing the Parul SE-lab
  PDF as the idea — hence SecureScan doubles as lab Practicals 1–4.
- Lesson bodies were scraped from `kiro.dev/2026/university` embedded JSON (page is
  JS-heavy; fetcher returned shell only). Extracts: `/tmp/lessons/` (not in git).
- 5,250 is impossible on free plan (Bonus 1 = paid only); target is 5,000 —
  documented in README + SUBMIT + CLOUD. Don't promise 5,250.
- Video is a REAL end-to-end recording (~2m15s, 873 CDP screenshots @30fps):
  register → scan → reports → history → GitHub .kiro evidence → 16/16 tests, with
  on-screen banners. Source frames/script: `demo/v2/`. Re-record only if behavior
  changes (then re-clobber the `final-demo` asset so the URL in SUBMIT.md holds).
- Commit history was rewritten (git filter-branch) so ALL commits are authored by
  `Alaqmar-morawala <232421638+Alaqmar-morawala@users.noreply.github.com>` — the
  parul email maps to the `saif-pvt` GitHub account (second account, disallowed).
  Local git config now uses the noreply address; NEVER reintroduce the parul email.


## 10. Real ZAP engine upgrade (2026-09-25, pre-freeze)

The app previously shipped fabricated findings only (`MockZapClient`); the
"real" client was a stub that raised. It is now real:

- `scanner/zap_client.py` — `RealZapClient`: ZAP session reset, spider
  (depth + page budget), passive-scan drain (pscan endpoint on ZAP ≥2.17,
  core fallback), active scan, paginated alerts, urllib3 Retry adapter,
  scan budget/deadline, progress callbacks. Severity mapping handles BOTH
  ZAP risk formats (numeric codes and 2.17+ string names) — this bit us
  once: real ZAP 2.17 returns "High"/"Medium"/... not 0-3.
- `scanner/zap_process.py` + `manage.py zap up|status|stop` — local daemon
  autostart/reuse (pidfile-tracked, /tmp logs), loopback + keyless by default.
- `scanner/engine.py` — engine selection: `SECURESCAN_MOCK=1|0|auto`;
  auto uses real ZAP when reachable else demo fixtures; powers the header
  engine chip (context processor + CSS). Real runs execute in a background
  thread so the existing progress-polling UI streams live progress.
- `scanner/guards.py` — SSRF guard (blocks loopback/RFC1918/link-local/
  metadata/non-global literals + `.local/.internal`; DNS resolution at scan
  time). `SECURESCAN_ALLOW_PRIVATE_TARGETS=1` for local demos only.
- `scanner/crypto.py` — Fernet encryption at rest for
  `Target.secret_header_value` (enc1: prefix, legacy plaintext passthrough);
  optional auth-header injection into scans via ZAP Replacer.
- Task-11 backlog closed: admin registration, CSV export, PDF executive
  summary, history pagination, estimate edge PBT, secret-header tests.
- `manage.py vuln_target` — bundled deliberately-vulnerable demo app
  (reflected/DOM XSS, error-based SQLi signature, missing headers, insecure
  cookie, verbose banner) so real scans have something true to find.
- Tests: `tests/fake_zap.py` (in-process fake ZAP API), new suites
  (65 offline total), `RUN_ZAP_E2E=1 tests/test_real_zap_integration.py`
  performs a REAL daemon-backed scan.
- Evidence: `demo/real-scan/{report.pdf,report.csv,findings.txt}` — a real
  full-stack `run_scan` run (SECURESCAN_MOCK=0) against the vulnerable
  target: High XSS (reflected+DOM, CWE-79), High SQLi (CWE-89), Medium CSP/
  clickjacking, Low cookie/banner/XCTO.

Reproduce the real-scan demo: `python3 manage.py zap up`, then
`python3 demo_real_scan.py` (forces SECURESCAN_MOCK=0, runs the vulnerable
target + a full scan, writes demo/real-scan/).
