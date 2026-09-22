# ZAP severity reference (see `scanner/services.py::SEVERITY_RANK`)

- High (4): XSS, SQLi — fix immediately, parameterized queries + output encoding.
- Medium (3): missing security headers — add CSP, X-Content-Type-Options.
- Low (2): cookie flags — Secure + HttpOnly + SameSite.
- Info (1): version disclosure — suppress banners.

Reports always sort by rank desc, then name asc (property P2).
