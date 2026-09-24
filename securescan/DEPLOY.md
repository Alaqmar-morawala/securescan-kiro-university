# Deploying SecureScan on Vercel

Serverless demo deployment of the Django app. **Mock mode** (`SECURESCAN_MOCK=True`)
means no Docker and no network egress — the whole flow works on a Vercel lambda.

## What is configured

| Concern | Setting / file |
|---|---|
| Entrypoint | `vercel.json` -> `@vercel/python` on `config/wsgi.py`; `app = application` |
| Runtime deps | `requirements.txt` (Django, reportlab, whitenoise) |
| Static files | WhiteNoise middleware + `WHITENOISE_USE_FINDERS=True` — serves `static/` directly, **no collectstatic build step** |
| Database | Ephemeral SQLite at `/tmp/db.sqlite3`; schema created on cold start by `config/wsgi.py` (`migrate`) |
| Secrets | `SECRET_KEY` env var (dev fallback only) |
| Hosts | `ALLOWED_HOSTS=['.vercel.app', 'testserver']` + `CSRF_TRUSTED_ORIGINS=['https://*.vercel.app']` |
| HTTPS | Vercel edge TLS; `SECURE_PROXY_SSL_HEADER`, `SECURE_SSL_REDIRECT`, modest HSTS (no includeSubDomains/preload on a shared host) |
| Debug | `DEBUG=false` when `VERCEL=1` |

## Deploy from the CLI

Vercel's **Root Directory must be `securescan`** (the repo root also holds `demo/` and docs).

```bash
cd securescan
npx vercel login                      # once, interactive
npx vercel                            # preview deploy
npx vercel --prod                     # production deploy
```

Optional env vars (Vercel dashboard -> Settings -> Environment Variables):

| Var | Purpose |
|---|---|
| `SECRET_KEY` | Recommended. Without it the dev fallback key is used. |
| `DEBUG` | `false` (default on Vercel). `true` only for debugging a preview. |
| `DATABASE_URL` | Postgres DSN; needs a driver (`psycopg[binary]`) added to `requirements.txt`. |
| `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` | Comma-separated extras for a custom domain. |

## Deploy from the dashboard

1. vercel.com -> Add New -> Project -> import the GitHub repo.
2. **Root Directory: `securescan`**. Framework preset: Other.
3. Build & Output settings: leave defaults (no build command needed).
4. Add the `SECRET_KEY` env var, then Deploy.

## Verify a deployment

```bash
BASE=https://<your-deployment>.vercel.app
curl -s -o /dev/null -w '%{http_code}\n' $BASE/                      # 200 landing
curl -s -o /dev/null -w '%{http_code}\n' $BASE/static/css/securescan.css  # 200 static
```

Then walk the app: register -> add website -> configure -> start scan ->
HTML/PDF report -> history. First request after idle is slower (cold start
runs `migrate`), subsequent requests are warm.

## Known limits (by design)

- **Ephemeral data**: each cold start gives a fresh `/tmp` DB, so demo accounts
  and scans reset. Add `DATABASE_URL` (Postgres/Neon) for persistence.
- **Real ZAP/Docker path is disabled**: serverless has no Docker daemon. The
  real path lives in `scanner/docker_runner.py` and raises unless
  `SECURESCAN_MOCK` is turned off on a Docker-capable host.
- **`check --deploy` warnings W005/W021** are intentional: HSTS
  `includeSubDomains`/`preload` are skipped because `*.vercel.app` is a shared
  domain.
