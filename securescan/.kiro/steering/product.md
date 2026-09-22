---
inclusion: always
---

# SecureScan — Product & Architecture Steering

SecureScan is a Django SaaS that lets users scan web apps they own for common
vulnerabilities (XSS, SQLi, misconfigurations) using OWASP ZAP in isolated
Docker containers, with cost estimation, progress monitoring, and PDF/HTML reports.

## Stack (must follow)
- Backend: Django 5.x, Django ORM, SQLite (dev) / PostgreSQL (prod via env)
- Frontend: Django templates + Bootstrap 5 (CDN allowed), no SPA framework
- Scanner: OWASP ZAP via REST API; Docker SDK for per-scan containers
- Reports: reportlab (PDF), Django templates (HTML)
- Tests: pytest + hypothesis for property-based tests

## Conventions
- Apps: `accounts` (auth/dashboard), `scanner` (targets, configs, scans, ZAP client),
  `reports` (report build/export). Keep business logic in `services.py` per app.
- All user input validated with Django forms; URLs validated with
  `URLValidator` + scheme allowlist (http/https only).
- NEVER scan arbitrary third-party hosts in automated tests; tests use mock ZAP client.
- Secrets via environment variables only; never commit `.env`.
- Every new view needs: URL route, login-required where appropriate,
  template, and at least one test.
