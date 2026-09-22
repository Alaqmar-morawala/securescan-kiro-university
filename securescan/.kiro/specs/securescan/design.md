# SecureScan — Design

## Architecture
Browser -> Django (accounts, scanner, reports apps) -> SQLite/Postgres
  -> Docker Engine (per-scan ZAP container) -> OWASP ZAP REST API
  -> findings -> report builder (HTML + reportlab PDF)

## Data model
- `Target(id, owner FK, name, url, secret_header_name?, secret_header_value?, created_at)`
- `ScanConfig(id, target FK, scan_type[baseline|spider|active|full], spider_depth 0-5, max_pages, created_at)`
- `Scan(id, owner FK, target FK, config FK, status[QUEUED|RUNNING|DONE|FAILED], progress 0-100, cost_estimate, duration_estimate_s, error?, created_at, finished_at?)`
- `Finding(id, scan FK, name, severity[High|Medium|Low|Info], url, description, solution, cwe?)`

## Components
- `scanner/services.py`: `estimate_cost(pages, depth, scan_type)` weights
  baseline=1, spider=2, active=4, full=6; cost = base + pages*depth*weight*factor.
- `scanner/zap_client.py`: `ZapClient` (real REST) + `MockZapClient` (deterministic
  fixtures for dev/tests/demo without network or Docker).
- `scanner/docker_runner.py`: `run_scan_container(...)` with try/finally cleanup;
  falls back to mock when Docker unavailable (env `SECURESCAN_MOCK=1`).
- `reports/services.py`: `order_findings()` severity sort; `build_html()`,
  `build_pdf()` via reportlab.
- `accounts/views.py`: register/login/logout/dashboard (LoginRequiredMixin).

## API / URLs
- `/` landing, `/accounts/register|login|logout`, `/dashboard`
- `/targets/add`, `/targets/<id>/configure`, `/targets/<id>/estimate`
- `/scans/<id>/start`, `/scans/<id>/progress` (JSON), `/scans/<id>/`
- `/scans/<id>/report.html`, `/scans/<id>/report.pdf`, `/history`

## Correctness (PBT via hypothesis)
- P1 monotonic cost: `for all pages1<=pages2, depth1<=depth2: est1 <= est2` (same type).
- P2 severity sort: output severities are non-increasing in rank order.
- P3 history order: `Scan.objects.filter(owner=u).order_by('-created_at')` equals view order.

## Test plan
- Example tests: auth flow, target validation, estimate view, start scan (mock),
  report PDF magic bytes `%PDF`, history isolation.
- Property tests: `tests/test_properties_cost.py`, `test_properties_report.py`,
  `test_properties_history.py` with hypothesis (>=100 examples).
