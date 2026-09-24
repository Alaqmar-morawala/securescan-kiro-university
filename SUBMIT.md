# Kiro University Challenge 2026 — Submission checklist (SecureScan)

## Links
- Repo: https://github.com/Alaqmar-morawala/securescan-kiro-university
- Demo video (real E2E, ~2m15s): https://github.com/Alaqmar-morawala/securescan-kiro-university/releases/download/final-demo/securescan-demo-real.mp4
  — regenerate with `demo/v2/record.sh` + `demo/v2/assemble.sh` (CDP screencast), then
  `gh release delete final-demo -y && git push origin :refs/tags/final-demo && gh release create final-demo demo/v2/securescan-demo-real.mp4`.
- Terms: https://kiro.dev/2026/university/terms/

## Still TODO (needs YOU — I can't post as you)
1. **Social post (X or LinkedIn)** — required. Must include:
   - repo link, 2–3 sentence description, `#KiroUniversity` + `#BuildWithKiro`,
     tag `@kirodotdev` (X) or `@kiro` (LinkedIn), + public demo video link above.
   - Final, character-checked copy for both networks: [`SOCIAL.md`](SOCIAL.md).
   - Post from the account matching GitHub user `Alaqmar-morawala`, then paste
     the public post URL into the entry form.
2. **Entry form** (opens Fri Sep 25 at https://kiro.dev/2026/university) — submit by
   **Mon Oct 5, 23:59 PT** with: GitHub repo link, demo video link, social post link,
   2–3 sentence description, per-lesson writeup (use `securescan/README.md` evidence map),
   correct contact email.
3. **Commit freeze**: NO commits to the repo after Oct 5 23:59 PT until judging ends
   (Oct 19) or you get the award email — else disqualification risk.

## Lesson writeup (paste into form)
- L1 Specs (250): `.kiro/specs/securescan/` — EARS requirements, design, tasks.
- L2 Steering (250): `.kiro/steering/` product/tech/testing with inclusion modes.
- L3 Hooks (250): `.kiro/hooks/python-checks.json` PostFileSave automation.
- L4 PBT IDE-only (500): `tests/test_properties_*.py` hypothesis ≥100 examples + example tests.
- L5 Powers (500): `powers/secscan-django/` installed + used via secscan/zap keywords.
- L6 MCP (1000): `.kiro/settings/mcp.json` fetch + power `mcp.json`.
- L7 Custom agents (1000): `.kiro/agents/` reviewer + zap-operator.
- Bonus 2 create-a-power (250): `powers/secscan-django/` original power.
- Bonus 1 cloud (250, paid only): NOT claimed, free plan — see `securescan/CLOUD.md`.
- Expected total: **5,000 credits** (5,250 with paid cloud).
