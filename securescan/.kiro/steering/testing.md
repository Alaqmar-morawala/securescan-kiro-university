---
inclusion: fileMatch
fileMatchPattern: "**/test*.py"
---

# SecureScan — Testing Standards

- Use pytest with `pytest-django` style markers; property tests with hypothesis.
- Property-based tests live in `tests/test_properties_*.py` and MUST state the
  property they check, e.g.:
  `Property: cost estimate is monotonic in (pages, depth, scan_type weight)`.
- Each spec requirement has at least one example test AND, where numeric or
  ordering logic exists, one property test with >= 100 examples.
- Scanner tests never hit network: use `scanner/zap_client.py::MockZapClient`.
- Run: `python -m pytest -q`.
