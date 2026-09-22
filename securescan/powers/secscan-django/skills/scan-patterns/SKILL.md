---
name: scan-patterns
description: Secure Django ZAP scan workflow — estimate, isolate, triage, report
---

# Scan Patterns Skill

Use when the user mentions `secscan`, `zap`, `owasp`, or `vulnerability scan`.

## Step 1: Validate target
- Require http/https URL the user owns; reject anything else.

## Step 2: Estimate
- Call `scanner.services.estimate_cost(pages, depth, scan_type)`; show cost + duration.

## Step 3: Isolate
- Run each scan in its own Docker container (`scanner/docker_runner.py`);
  always cleanup in `finally`; use `MockZapClient` when `SECURESCAN_MOCK=1`.

## Step 4: Triage + report
- Order with `order_findings()` (High > Medium > Low > Info).
- Export HTML + PDF via `reports/services.py`.
