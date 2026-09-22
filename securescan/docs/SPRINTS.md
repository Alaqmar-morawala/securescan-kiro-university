# SecureScan — Agile Sprint Timeline (Practical 2)

6 sprints, mapped to the `.kiro/specs/securescan/tasks.md` checklist.

| Sprint | Focus | Shipped as |
|---|---|---|
| 1 | Requirement analysis, auth, database | `scanner/models.py` (Target/ScanConfig/Scan/Finding), `accounts/` register/login, migration `0001_initial` |
| 2 | Dashboard, website registration, scan configuration | `DashboardView`, `TargetCreateView`, `ScanConfigView` + cost estimate via `estimate_cost()` |
| 3 | Docker integration + OWASP ZAP | `scanner/zap_client.py` (Mock + real), `docker_runner.run_scan()` with `finally` container cleanup |
| 4 | Vulnerability reports + scan history | `reports/services.build_pdf_bytes()`, HTML/PDF views, `ScanHistoryView` (newest-first) |
| 5 | Pricing engine + secret-header auth | `estimate_cost()` weights (baseline 1 / spider 2 / active 4 / full 6), per-target `secret_header_*` fields |
| 6 | Testing, deployment + docs | `tests/` (5 example + 4 property), `README.md`, `ARCHITECTURE.md`, mock-mode deploy notes |

## Why Agile (from lab Practical 2)

Independent modules (auth, dashboard, Docker/ZAP, reports, pricing) ship per
sprint; continuous testing after each sprint keeps quality high; changing
security requirements fit iterative planning. See `.kiro/specs/securescan/`
for the living spec this timeline implements.
