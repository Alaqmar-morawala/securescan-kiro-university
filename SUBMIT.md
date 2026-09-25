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

## Lesson writeup (paste into form)
> Context line you can prepend: "SecureScan is a Django SaaS that runs real
> OWASP ZAP scans (with a deterministic offline demo mode), 65 offline tests,
> and ships its full .kiro evidence in the repo. Demo video shows a live ZAP
> scan finding real High-severity XSS + SQLi."
- L1 Specs (250): `.kiro/specs/securescan/` — EARS requirements, design, 14-task list with completion state.
- L2 Steering (250): `.kiro/steering/` product/tech/testing with inclusion modes.
- L3 Hooks (250): `.kiro/hooks/python-checks.json` — PostFileSave compile check + pytest smoke (both still pass on the current tree).
- L4 PBT IDE-only (500): `tests/test_properties_{cost,report,history}.py` — hypothesis, 100–200 examples per property, including edge-input clamping PBT over the estimator and ordering invariants over the real report/severity pipeline.
- L5 Powers (500): `powers/secscan-django/` installed + used via secscan/zap keywords.
- L6 MCP (1000): `.kiro/settings/mcp.json` fetch + power `mcp.json`.
- L7 Custom agents (1000): `.kiro/agents/` reviewer + zap-operator.
- Bonus 2 create-a-power (250): `powers/secscan-django/` original power.
- Bonus 1 cloud (250, paid only): NOT claimed, free plan — see `securescan/CLOUD.md`.
- Expected total: **5,000 credits** (5,250 with paid cloud).

## Evidence quick-paths for reviewers
- Real scan (product works): `demo/real-scan/` — PDF/CSV + findings list from a
  full-stack `run_scan` run (SECURESCAN_MOCK=0) against the bundled vulnerable
  app; video shows the same flow live.
- Real engine code: `scanner/zap_client.py` (RealZapClient), `scanner/zap_process.py`,
  `scanner/engine.py`, `scanner/guards.py` (SSRF), `scanner/crypto.py` (secrets at rest).
- Tests: `python3 -m pytest tests/ -q` → 65 passed, 1 skipped (opt-in live ZAP test:
  `RUN_ZAP_E2E=1 pytest tests/test_real_zap_integration.py`).
