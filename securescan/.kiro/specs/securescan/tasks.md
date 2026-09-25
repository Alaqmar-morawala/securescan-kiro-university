# SecureScan — Tasks

- [x] 1. Scaffold Django project + apps (accounts, scanner, reports), settings, URLs
- [x] 2. Models: Target, ScanConfig, Scan, Finding + migrations
- [x] 3. Auth: register/login/logout/dashboard views + templates
- [x] 4. Targets: add/configure/estimate views + cost service
- [x] 5. Scanner: MockZapClient + real ZapClient stub + docker_runner with cleanup
- [x] 6. Scan run: start/progress/detail views (mock mode default)
- [x] 7. Reports: HTML + PDF export + history view
- [x] 8. Kiro lesson artifacts: steering, hooks, PBT, power install+create, MCP, agents
- [x] 9. Run test suite (example + property tests), fix failures (9/9 green)
- [x] 10. Demo video script + README lesson map + entry form submission (video public; form opens Sep 25)
- [x] 11. Hardening (pre-freeze, ≤ Oct 4): severity badges ✓(t13), progress auto-refresh ✓(t13), secret-header tests (tests/test_target_secrets.py), estimate edge PBT (tests/test_properties_cost.py), PDF executive summary (reports/services.py), history pagination, ZAP retries (zap_client Retry adapter), admin registration (scanner/admin.py), CSV export (/scans/<pk>/report.csv)
- [x] 12. P3 real PBT + hook smoke-test target (Sep 23): `test_history_newest_first_property` (hypothesis 100 examples,
  view+ORM ordering + owner isolation), `tests/test_smoke.py` wired to `hooks/python-checks.json` — 11/11 green
- [x] 13. Frontier UI + E2E lock-in (Sep 23): self-hosted dark theme (`static/css/securescan.css`, no Bootstrap CDN),
  severity badges (`sev-high/medium/low/info`), status chips, live progress polling (`data-progress-url` + `static/js/securescan.js`),
  fixed `ScanDetailView` KeyError (`ctx["findings"]` never existed for DetailView); new `tests/test_ui_frontier.py`
  (5 tests: full flow, severity order, progress contract, cross-user 404s, PDF auth) — 16/16 green


- [x] 14. Real ZAP engine (Sep 25, pre-freeze): full REST client in `scanner/zap_client.py` (session reset, spider w/ depth+page budget, passive drain, active scan, paginated alerts, retry adapter, poll deadlines, risk-name+numeric severity mapping), daemon lifecycle `scanner/zap_process.py` + `manage.py zap`, engine selection `scanner/engine.py` (mock/auto/real + UI chip), background-thread scan runs with live progress, SSRF target guard `scanner/guards.py`, Fernet secret-at-rest `scanner/crypto.py`, admin registration, CSV export, PDF executive summary, history pagination, `manage.py vuln_target` demo app, fake-ZAP test server, opt-in live integration test (RUN_ZAP_E2E=1). Real-scan evidence: `demo/real-scan/`. Suite: 65 passed offline (was 16).
