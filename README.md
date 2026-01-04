# OutfitGuru Backend
FastAPI + SQLite API that powers OutfitGuru. Handles auth, wardrobe storage, rule-based outfit recommendations, feedback, and history.

## Stack
- FastAPI, Pydantic v2, SQLAlchemy
- JWT auth via python-jose + passlib (bcrypt)
- SQLite (file: `outfitguru.db`)

## Branch policy
- `main` is protected; do all work on feature branches (or `dev`) and merge via PRs.
- Local safeguard: `git config core.hooksPath .githooks` (blocks direct pushes to `main`).

## Requirements
- Python 3.12 (pinned at 3.12.12 via `.python-version`)
- `virtualenv`/`venv` available

## Setup
```bash
cd /Users/het/Projects/outfitguru/outfitguru-backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set secrets before running
uvicorn app.main:app --reload --port 8000
```
API: http://127.0.0.1:8000  
Docs: http://127.0.0.1:8000/docs

## Environment
- `OUTFITGURU_SECRET_KEY` (required; set to a strong value for any shared environment)
- Optional:
  - `OUTFITGURU_DATABASE_URL` (default `sqlite:///./outfitguru.db`)
  - `OUTFITGURU_CORS_ORIGINS` (default `["http://localhost:5173"]`)

`.env.example` provided as a starting point. Do not commit real secrets.

## API Overview
- **Auth**
  - `POST /auth/register` — `{email, password}` → user + token
  - `POST /auth/login` — `{email, password}` → token
  - `GET /me` — current user (Bearer token)
- **Wardrobe**
  - `GET /wardrobe/categories` — catalog of categories + subtypes + allowed color families/seasons
  - `POST /wardrobe/items` — create item (category, subtype, color family, season, optional notes/image_url)
  - `GET /wardrobe/items` — list items for the user
- **Outfits**
  - `POST /outfits/recommendation` — generate and persist today’s outfit, or return `need_more_items` payload when required categories are missing
  - `POST /outfits/{id}/feedback` — set feedback (`like`, `dislike`, `skip`, `none`)
  - `GET /outfits/history` — list outfits (most recent first)
- **Calendar**
  - `GET /calendar/month?year=YYYY&month=MM` — occurrences for the month
  - `GET /calendar/day?date=YYYY-MM-DD` — occurrence for a single day
  - `POST /calendar/plan-tomorrow` — copy latest outfit into tomorrow’s slot (idempotent)
  - `POST /calendar/confirm-worn` — mark a day worn/with reason if skipped

## Quick Testing
- Swagger UI: open http://127.0.0.1:8000/docs and try requests with “Authorize” (Bearer token).
- Curl flow:
```bash
# Register
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"secret123"}'

# Login
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"secret123"}' | jq -r '.access_token')

# Add wardrobe item
curl -X POST http://127.0.0.1:8000/wardrobe/items \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"category":"top","color":"navy","subtype":"General","color_family":"Blue","season":"All-season"}'

# Request recommendation
curl -X POST http://127.0.0.1:8000/outfits/recommendation \
  -H "Authorization: Bearer $TOKEN"

# Plan tomorrow (after at least one recommendation exists)
curl -X POST http://127.0.0.1:8000/calendar/plan-tomorrow \
  -H "Authorization: Bearer $TOKEN"
```

## Database Notes
- Defaults to SQLite file `outfitguru.db` in the repo root.
- Change `OUTFITGURU_DATABASE_URL` for external DBs; built-in lightweight SQLite migration adds wardrobe metadata columns if missing.

## Common Issues
- **Address already in use (8000):** stop existing uvicorn or change `--port`.
- **Wrong Python version:** install/use Python 3.12+ for compatibility.
- **Missing `pydantic-settings` or other deps:** ensure the virtualenv is active and `pip install -r requirements.txt` succeeded.

## Security
- Always set a strong `OUTFITGURU_SECRET_KEY`; rotate if exposed.
- Keep `.env` out of version control; only commit `.env.example`.

## Production notes
- Required env vars: `OUTFITGURU_SECRET_KEY`, `OUTFITGURU_DATABASE_URL`, `OUTFITGURU_CORS_ORIGINS`.
- Run without reload for production: `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- Set CORS to your deployed frontend origin(s); avoid `"*"`.
- Rotate `OUTFITGURU_SECRET_KEY` if compromised; tokens issued before rotation will become invalid.

## Auth rules (staging)
- Passwords: minimum length 8; stored as bcrypt hashes (no plaintext).
- Tokens: JWT access token ~24h expiry (`access_token_expire_minutes`); expired/invalid/missing token returns 401.
- Duplicate email on register returns 409; invalid credentials return 401.
- Errors: JSON responses with `detail` and appropriate status codes.

## Deploying on Render
- Service type: Web Service (Python).
- Build: Render installs from `requirements.txt`; no extra build step.
- Start command:
  ```
  uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```
- Health check: `/health`.
- Env vars:
  - `OUTFITGURU_SECRET_KEY` (required, strong)
  - `OUTFITGURU_DATABASE_URL` (use Neon Postgres in prod)
  - `OUTFITGURU_CORS_ORIGINS` (JSON array; include your frontend origin)
  - `ENV` (optional, e.g., `production`)

## Production environment variables
- `OUTFITGURU_SECRET_KEY` — required
- `OUTFITGURU_DATABASE_URL` — Postgres for prod; SQLite only for local dev
- `OUTFITGURU_CORS_ORIGINS` — JSON array of allowed origins
- `ENV` — optional flag for environment

## Production run command
```
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## CORS configuration
- Dev: include `http://localhost:5173`.
- Prod: set to your Cloudflare Pages domain(s); do not use `"*"` in production.

## Database configuration
- Local: SQLite file `outfitguru.db`.
- Production: set `OUTFITGURU_DATABASE_URL` to a Postgres connection string (e.g., Neon).

## Health endpoint
- `GET /health` → `{"status":"ok"}`. Use for Render health checks.
