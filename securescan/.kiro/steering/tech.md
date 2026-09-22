---
inclusion: always
---

# SecureScan — Python/Django Code Standards

- Python 3.12+, Django 5.x. Type hints on all service functions.
- Formatting: black-compatible style, max line length 100, double quotes.
- Imports order: stdlib, third-party (django, ...), local apps.
- Models: explicit `__str__`, `Meta.ordering` where listing matters,
  indexes on foreign keys used in filters (`Scan.owner`, `Scan.target`).
- Views: prefer class-based views; use `LoginRequiredMixin` for user areas.
- Forms validate everything; never trust raw `request.POST`.
- Security: password hashing via Django auth, CSRF on all POST, secret-header
  value stored per target and sent only to that target's scan job.
- Error handling: wrap Docker/ZAP calls, mark scan FAILED with message,
  always cleanup containers in `finally`.
