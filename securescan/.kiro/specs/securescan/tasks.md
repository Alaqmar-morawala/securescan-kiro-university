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
- [ ] 11. Hardening (pre-freeze, ≤ Oct 4): severity badges, progress auto-refresh, secret-header tests, estimate edge PBT, PDF summary, pagination, ZAP retry, admin registration, CSV export
- [x] 12. P3 real PBT + hook smoke-test target (Sep 23): `test_history_newest_first_property` (hypothesis 100 examples,
  view+ORM ordering + owner isolation), `tests/test_smoke.py` wired to `hooks/python-checks.json` — 11/11 green
- [x] 13. Frontier UI + E2E lock-in (Sep 23): self-hosted dark theme (`static/css/securescan.css`, no Bootstrap CDN),
  severity badges (`sev-high/medium/low/info`), status chips, live progress polling (`data-progress-url` + `static/js/securescan.js`),
  fixed `ScanDetailView` KeyError (`ctx["findings"]` never existed for DetailView); new `tests/test_ui_frontier.py`
  (5 tests: full flow, severity order, progress contract, cross-user 404s, PDF auth) — 16/16 green

