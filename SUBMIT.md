# Kiro University Challenge — Submission checklist (SecureScan)

## Links
- Repo: https://github.com/Alaqmar-morawala/securescan-kiro-university
- **Demo video (real engine, 1m54s):** https://github.com/Alaqmar-morawala/securescan-kiro-university/releases/download/final-demo/securescan-demo-real-engine.mp4
  — real OWASP ZAP scan of the bundled vulnerable app: live progress, 37 real
  findings (High XSS + SQLi), per-lesson .kiro tour, 65-test outro. The scan
  segment is time-lapsed ~0.3x to fit the 3-minute cap (wall time was ~110s).
  Older asset (mock-mode E2E, ~2m15s): `securescan-demo-real.mp4` on the same
  `final-demo` release.
  Regenerate with: ZAP up (`manage.py zap up`) + `manage.py vuln_target` +
  `SECURESCAN_MOCK=0 SECURESCAN_ALLOW_PRIVATE_TARGETS=1 manage.py runserver
  127.0.0.1:8472`, then `demo/v2/record_real.sh` (CDP screencast + ffmpeg).
- Terms: https://kiro.dev/2026/university/terms/ (re-verified 2026-09-25:
  video 30s–3min showing the project + each lesson; form = repo link, public
  video, social post link, per-lesson writeup, correct email; freeze after
  Oct 5 23:59 PT until ~Oct 19).

## Still TODO (needs YOU — I can't post as you)
1. **Social post (X or LinkedIn)** — required. Must include:
   - repo link, 2–3 sentence description, `#KiroUniversity` + `#BuildWithKiro`,
     tag `@kirodotdev` (X) or `@kiro` (LinkedIn), + public demo video link above.
   - Final, character-checked copy for both networks: [`SOCIAL.md`](SOCIAL.md).
   - Post from the account matching GitHub user `Alaqmar-morawala`, then paste
     the public post URL into the entry form.
2. **Entry form** (open now at https://kiro.dev/2026/university) — submit by
   **Mon Oct 5, 23:59 PT** with: GitHub repo link, demo video link, social post link,
   2–3 sentence description, per-lesson writeup (below / `securescan/README.md`
   evidence map), correct contact email.
3. **Commit freeze**: NO commits to the repo after Oct 5 23:59 PT until judging ends
   (Oct 19) or you get the award email — else disqualification risk.

## Lesson writeup (paste into form — judge-facing, full text)

> Context sentence you can prepend: "SecureScan is a Django SaaS that runs real
> OWASP ZAP scans (with a deterministic offline demo mode); 65 offline tests;
> the full .kiro evidence ships in the repo and the demo video shows a live
> scan finding real High-severity XSS + SQLi."

1. Spec-driven development — SecureScan was built spec-first in Kiro:
   `.kiro/specs/securescan/requirements.md` (EARS-style requirements),
   `design.md` (architecture decisions: Django apps, engine selection, report
   pipeline) and `tasks.md` (14-task list with per-task completion state).
   The build followed the task list top-to-bottom — each implementation phase
   is a commit referencing the spec work.
2. Steering documents — `.kiro/steering/` with inclusion frontmatter:
   `product.md` (mission, users, non-goals), `tech.md` (Django 5/SQLite/
   reportlab stack + conventions), `testing.md` (offline-deterministic test
   policy). Kiro loaded these as persistent context on every session.
3. Hooks — `.kiro/hooks/python-checks.json` defines two PostFileSave hooks:
   a `python -m compileall` syntax check on every saved .py file, and a
   `python -m pytest tests/test_smoke.py` smoke test whenever
   `scanner/services.py` changes. Both commands run clean on the current tree.
4. Property-based testing (IDE only) — `tests/test_properties_cost.py`,
   `test_properties_history.py`, `test_properties_report.py`: hypothesis
   properties with 100–200 generated examples each — estimator monotonicity
   and edge clamping (negative/oversized inputs), severity ordering invariant
   (High>Medium>Low>Info), history newest-first + owner isolation. Authored
   and run through Kiro; the offline suite is 65 tests, all green.
5. Powers — `powers/secscan-django/` is an in-repo Kiro power (plugin.json +
   skills/scan-patterns/SKILL.md + severity reference + mcp.json) that was
   installed into Kiro and invoked via secscan/zap/owasp keywords during the
   build; it encodes the project's scan-pattern and severity conventions.
6. Model Context Protocol (MCP) — `.kiro/settings/mcp.json` configures the
   fetch MCP server used during the build; the power bundles its own MCP
   config (`powers/secscan-django/mcp.json`, secscan-fetch). Used to pull
   OWASP/ZAP documentation while building the real engine.
7. Custom agents — `.kiro/agents/securescan-reviewer.json` (security-review
   policy: ownership checks on every view, never scan hosts you don't own,
   secret hygiene) and `zap-operator.json` (ZAP daemon lifecycle rules). The
   SSRF guard (`scanner/guards.py`) and encrypted secrets
   (`scanner/crypto.py`) implement these agent policies in code.

[Bonus] Kiro Web/cloud: not claimed — built entirely on the Kiro CLI free plan
(see `securescan/CLOUD.md`). Bonus power: same `powers/secscan-django/`
plugin.json (URL in the evidence quick-paths below).

## Evidence quick-paths for reviewers## Evidence quick-paths for reviewers
- Real scan (product works): `demo/real-scan/` — PDF/CSV + findings list from a
  full-stack `run_scan` run (SECURESCAN_MOCK=0) against the bundled vulnerable
  app; video shows the same flow live.
- Real engine code: `scanner/zap_client.py` (RealZapClient), `scanner/zap_process.py`,
  `scanner/engine.py`, `scanner/guards.py` (SSRF), `scanner/crypto.py` (secrets at rest).
- Tests: `python3 -m pytest tests/ -q` → 65 passed, 1 skipped (opt-in live ZAP test:
  `RUN_ZAP_E2E=1 pytest tests/test_real_zap_integration.py`).
