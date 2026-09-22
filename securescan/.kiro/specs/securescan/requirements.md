# SecureScan — Feature Spec

## Requirements

### REQ-1: User Management
- WHEN a visitor submits registration with name, email, password
  THE SYSTEM SHALL validate inputs and create an account, rejecting duplicate emails.
- WHEN a user submits valid credentials THE SYSTEM SHALL authenticate and
  redirect to the dashboard within 2 seconds.
- WHEN credentials are invalid THE SYSTEM SHALL show a field-level error.

### REQ-2: Target & Scan Configuration
- WHEN a logged-in user adds a website URL THE SYSTEM SHALL validate it
  (http/https) and list it on the dashboard.
- WHEN a user configures a scan (scan_type, spider_depth 0-5, auth optional,
  secret header optional) THE SYSTEM SHALL persist the configuration.
- WHEN a user requests a cost estimate THE SYSTEM SHALL return estimated
  cost + duration derived from pages/depth/scan-type weights.

### REQ-3: Scan Execution (Docker + ZAP)
- WHEN a user starts a scan THE SYSTEM SHALL create an isolated Docker
  container running OWASP ZAP (or mock client in dev), start spider + active
  scan within 10s, stream progress, and collect alerts.
- WHEN Docker/ZAP fails THE SYSTEM SHALL mark scan FAILED, store the error,
  and cleanup the container.

### REQ-4: Reports & History
- WHEN a scan completes THE SYSTEM SHALL generate severity-classified
  findings (High/Medium/Low/Info) within 30s and render HTML.
- WHEN a user clicks Export PDF THE SYSTEM SHALL return a PDF report.
- WHEN a user opens History THE SYSTEM SHALL list past scans newest-first,
  visible only to the owner.

### REQ-5: Security
- WHEN any scan runs THE SYSTEM SHALL require authentication and ownership
  of the target; support per-target secret header auth.

## Correctness properties (PBT scope)
- P1: Cost estimate monotonic in pages, depth, scan-type weight.
- P2: Severity ordering High > Medium > Low > Info preserved in report sort.
- P3: Scan history ordering newest-first invariant.
