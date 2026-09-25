# Social posts — Kiro University Challenge (SecureScan)

> **Human-only:** I cannot post as you. Copy the text below, post it from the
> account that matches your GitHub (`Alaqmar-morawala`), then paste the post URL
> into the entry form.

## The requirement (verbatim from the terms)

> **7.** Post your submission on either X or LinkedIn with **#KiroUniversity** and
> **#BuildWithKiro**, and tag **@kirodotdev** on X or **@kiro** on LinkedIn.
>
> **8.** Your post must include: public GitHub repo link, short description (2-3
> sentences)…

Terms: https://kiro.dev/2026/university/terms/

**Both links go in the post** (repo + demo video) so item 8 is satisfied on any
reading of the truncated clause.

## ⚠️ Read before posting

| Rule | Why it matters |
|---|---|
| Post from the account matching GitHub **`Alaqmar-morawala`** | "GitHub accounts not matching social accounts may be disqualified." Never use the second authed account (`saif-pvt`). |
| Post must be **public** and stay public | The entry form needs a link judges can open; deleting it later risks the entry. |
| Tag the right handle | `@kirodotdev` on X, `@kiro` on LinkedIn — they're different. |
| Both hashtags, exact spelling | `#KiroUniversity` and `#BuildWithKiro`. |
| **Don't commit to the repo after Oct 5 23:59 PT** | Commit freeze until judging ends (~Oct 19). Editing the post is fine; pushing code is not. |

---

## Option A — X / Twitter ✅ fits 280 (275 by X's URL weighting, URLs = 23)

```
SecureScan: real OWASP ZAP scans (spider + active) on apps you own, with cost estimates and severity-ordered HTML/PDF/CSV reports — plus offline demo mode. Built spec-first with Kiro.

#KiroUniversity #BuildWithKiro @kirodotdev
https://github.com/Alaqmar-morawala/securescan-kiro-university
https://github.com/Alaqmar-morawala/securescan-kiro-university/releases/download/final-demo/securescan-demo-real-engine.mp4
```

**Verified:** 275 characters by X's URL weighting (each URL counts as 23),
414 raw characters. Both links return HTTP 200. Updated 2026-09-25 for the
real-engine build (replaces the mock-mode copy).

## Option B — LinkedIn ✅

```
I built SecureScan, a Django web-security scanner for the Kiro University Challenge that runs real OWASP ZAP scans — spider, passive and active rules — against the apps you own, with per-scan cost estimates, an SSRF guard that blocks internal targets, and severity-ordered HTML, PDF and CSV reports. With no ZAP daemon running it falls back to a deterministic offline demo mode, so the whole workflow still runs without network access.

I developed it spec-first with Kiro using EARS requirements, steering documents, automated hooks, Hypothesis property-based tests, a custom power, MCP configuration, and specialist review/scanning agents; the 65-test suite covers the real ZAP client, the SSRF guard, cost estimation, report ordering, owner isolation, and the complete UI flow — and the demo video shows a live ZAP scan finding real High-severity XSS and SQL injection.

Repo: https://github.com/Alaqmar-morawala/securescan-kiro-university
Demo video (1m54s): https://github.com/Alaqmar-morawala/securescan-kiro-university/releases/download/final-demo/securescan-demo-real-engine.mp4

#KiroUniversity #BuildWithKiro @kiro
```

## Posting checklist

1. Open X or LinkedIn and confirm the account identity matches GitHub user
   `Alaqmar-morawala`.
2. Copy **Option A** for X or **Option B** for LinkedIn exactly.
3. Verify the platform preview shows both links and the correct platform tag.
4. Post publicly, open the post in a private/incognito window, and save its URL.
5. Paste that URL into the challenge entry form.

Do not use the alternate authenticated `saif-pvt` account: mismatched social and
GitHub identities may be disqualified.
