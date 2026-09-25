# SecureScan — Web Application Security Scanner (SaaS)

**Kiro University Challenge 2026 — Final Exam submission.**
Built with Kiro (CLI) as the primary development tool. Django + a real
OWASP ZAP engine (deterministic demo fixtures as offline fallback) +
severity-ordered HTML/PDF/CSV reports.

## Quickstart
```bash
python3 manage.py migrate
python3 manage.py runserver
# register -> Add website -> Configure scan -> Start scan -> HTML/PDF/CSV report
```
Without a ZAP daemon the app auto-falls back to deterministic demo fixtures
(fully offline — no Docker or network needed for judges); the active engine
is shown in the header chip.

## Real scan engine (live OWASP ZAP)

The real path is fully implemented — session isolation, spider with
depth/page budget, passive-scan drain, active scan, paginated alert
collection, retries, and an optional authenticated-scan header (ZAP
Replacer). Evidence from an actual run: `../demo/real-scan/`.

```bash
python3 manage.py zap up          # start (or reuse) a local ZAP daemon
python3 manage.py vuln_target     # bundled deliberately-vulnerable demo app
# in another shell:
SECURESCAN_MOCK=0 SECURESCAN_ALLOW_PRIVATE_TARGETS=1 python3 manage.py runserver
```

Engine selection (`SECURESCAN_MOCK`): `1` force demo fixtures, `0` force
real ZAP (scan fails if the daemon is unreachable), unset/`auto` (default)
uses real ZAP when reachable and falls back otherwise. Real scans run in a
background thread; the detail page streams progress via polling.

| Env var | Default | Purpose |
|---|---|---|
| `SECURESCAN_MOCK` | `auto` | Engine selection (see above) |
| `SECURESCAN_ZAP_HOST` / `SECURESCAN_ZAP_PORT` | `127.0.0.1:8090` | Daemon address |
| `SECURESCAN_ZAP_API_KEY` | empty | ZAP API key (daemon runs keyless+loopback by default) |
| `SECURESCAN_ZAP_AUTOSTART` | `false` | Let `run_scan` launch/reuse a local daemon |
| `SECURESCAN_ZAP_LAUNCHER` | `local` | `local` binary or `docker` per-scan container |
| `SECURESCAN_ALLOW_PRIVATE_TARGETS` | off | Allow loopback/RFC1918 targets (local demos ONLY) |

The SSRF guard (`scanner/guards.py`) blocks non-public targets (loopback,
RFC1918, link-local incl. cloud metadata, `.local`/`.internal` names) on
every real scan. Secret header values are encrypted at rest (Fernet).
Tests: `RUN_ZAP_E2E=1 pytest tests/test_real_zap_integration.py` performs a
real daemon-backed scan of the bundled vulnerable target.

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
3. Start scan → progress JSON → DONE with severity-ordered findings.
4. Open HTML report → Download PDF / CSV.
5. History page. Then flash `.kiro/` tree: specs, steering, hooks, agents, settings/mcp.json + `powers/secscan-django/`.
6. (Optional, if ZAP is running) same flow against `manage.py vuln_target` with real findings.

## University project mapping (Parul SE lab)
Practical 1 (objectives/requirements) → `.kiro/specs/securescan/requirements.md`;
Practical 2 (Agile model + sprints) → `tasks.md` + `docs/SPRINTS.md`;
Practical 3 (SRS) → `requirements.md` + `design.md`;
Practical 4 (SPMP) → `docs/SPMP.md`.
