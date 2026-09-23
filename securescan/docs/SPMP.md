# SecureScan — Software Project Management Plan (Practical 4)

## 1. Objectives

Ship a SaaS where users scan web apps they own for OWASP Top-10 issues via
isolated ZAP containers, with cost estimates and HTML/PDF reports.
Non-goals: third-party scanning (authz enforced), real-time collaboration.

## 2. Schedule (Agile, 6 sprints)

See `SPRINTS.md`. Sprint exit criteria: spec tasks checked in
`.kiro/specs/securescan/tasks.md` + `pytest` green (currently 16/16).

## 3. Team & roles (coursework mapping)

Single-developer build; roles map to code areas: backend (`scanner/`,
`reports/`), frontend (`templates/`), QA (`tests/`), docs (`docs/`, `.kiro/`).

## 4. Resources

- Hardware: any i5+/8GB machine; dev runs SQLite, no GPU needed.
- Software: Python 3.12+, Django 5.x, Docker (prod scans only),
  `ghcr.io/zaproxy/zaproxy:stable`, reportlab, hypothesis, pytest-django.

## 5. Risk register

| Risk | Impact | Mitigation (implemented) |
|---|---|---|
| Docker misconfig | High | Mock mode (`SECURESCAN_MOCK=True`); real path fails loudly, cleanup in `finally` |
| Long scans | Medium | Cost/duration estimate upfront; progress endpoint; per-scan containers |
| Unauthorized scanning | High | Login required; owner-only queries; http/https allowlist; per-target secret header |
| Integration failures | Medium | `MockZapClient` for tests/demo; example + property tests per module |
| DB loss | High | SQLite dev / Postgres prod via env; history never deleted by scans |
| Requirement changes | Medium | Spec-first: change `requirements.md` → `design.md` → `tasks.md` |
| Time constraints | High | Mock-first vertical slice; hardening commits before Oct 4 freeze buffer |

## 6. Quality assurance

- Example tests: auth flow, target validation, estimate math, mock scan + PDF
  bytes, history isolation (`tests/test_example.py`).
- Property tests (hypothesis, ≥100 examples): P1 cost monotonicity, P2 severity
  ordering, P3 history newest-first (`tests/test_properties_*.py`).
- Gates per commit: `pytest -q`, `manage.py check`, manual smoke of
  register → add → configure → start → report → history.
