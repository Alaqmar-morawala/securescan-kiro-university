# SecureScan Architecture

Browser → Django (`accounts`, `scanner`, `reports`) → SQLite/Postgres
→ Docker Engine (one container per scan) → OWASP ZAP REST API
→ findings → `reports/services.py` (HTML + reportlab PDF).

Key files:
- `scanner/services.py` — `estimate_cost`, `order_findings` (+ P1/P2 properties)
- `scanner/zap_client.py` — `MockZapClient` (demo) + `ZapClient` (real REST)
- `scanner/docker_runner.py` — `run_scan` with try/finally container cleanup
- `reports/services.py` — severity-ordered PDF builder
