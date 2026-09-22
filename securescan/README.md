# SecureScan — Web Application Security Scanner (SaaS)

**Kiro University Challenge 2026 — Final Exam submission.**
Built with Kiro (CLI) as the primary development tool. Django + OWASP ZAP
(mock mode for demo; real Docker+ZAP path included) + severity-ordered HTML/PDF reports.

## Quickstart
```bash
python3 manage.py migrate
python3 manage.py runserver
# register -> Add website -> Configure scan -> Start scan -> HTML/PDF report
```
Mock mode (`SECURESCAN_MOCK=True` in `config/settings.py`) runs fully offline
with deterministic findings — no Docker or network needed for judges.

## Kiro lessons demonstrated (evidence map)
| Lesson | Where to look |
|---|---|
| 1. Spec-driven development (250) | `.kiro/specs/securescan/{requirements,design,tasks}.md` — EARS requirements, design, task list |
| 2. Steering documents (250) | `.kiro/steering/{product,tech,testing}.md` with `inclusion` frontmatter |
| 3. Hooks (250) | `.kiro/hooks/python-checks.json` — PostFileSave syntax check + smoke test |
| 4. Property-based testing, IDE-only (500) | `tests/test_properties_{cost,report,history}.py` (hypothesis, ≥100 examples) + `tests/test_example.py` |
| 5. Powers — install+use (500) | `powers/secscan-django/` installed in-repo power: `plugin.json` + `skills/scan-patterns/SKILL.md` + `mcp.json`; invoked via keywords secscan/zap/owasp |
| 6. MCP (1000) | `.kiro/settings/mcp.json` (fetch server) + `powers/secscan-django/mcp.json` (secscan-fetch) |
| 7. Custom agents (1000) | `.kiro/agents/securescan-reviewer.json`, `.kiro/agents/zap-operator.json` |
| Completion (all 7) | +1000 |
| Bonus 2 — create a power (250) | `powers/secscan-django/` is an original power created for this project (manifest + skill + refs + MCP) |
| Bonus 1 — cloud (paid only) | Free plan — see `CLOUD.md`. Not claimed. |

**Expected total on free plan: 5,000 credits** (5,250 with paid cloud bonus).


## Demo video script (60–90s)
1. Landing → register/login (auth).
2. Add `https://example.com` → configure (full, depth 3) → show cost/duration estimate.
3. Start scan → progress JSON → DONE with 5 severity-ordered findings.
4. Open HTML report → Download PDF.
5. History page. Then flash `.kiro/` tree: specs, steering, hooks, agents, settings/mcp.json + `powers/secscan-django/`.

## University project mapping (Parul SE lab)
Practical 1 (objectives/requirements) → `.kiro/specs/securescan/requirements.md`;
Practical 2 (Agile model + sprints) → `tasks.md` + `docs/SPRINTS.md`;
Practical 3 (SRS) → `requirements.md` + `design.md`;
Practical 4 (SPMP) → `docs/SPMP.md`.
