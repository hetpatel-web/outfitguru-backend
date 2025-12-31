# OutfitGuru Backend
FastAPI + SQLite API that powers OutfitGuru. Handles auth, wardrobe storage, rule-based outfit recommendations, feedback, and history.

## Stack
- FastAPI, Pydantic v2, SQLAlchemy
- JWT auth via python-jose + passlib (bcrypt)
- SQLite (file: `outfitguru.db`)

## Requirements
- Python 3.12+ (recommended)
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
  - `POST /wardrobe/items` — create clothing item (category, color, optional notes/image_url)
  - `GET /wardrobe/items` — list items for the user
- **Outfits**
  - `POST /outfits/recommendation` — generate and persist today’s outfit
  - `POST /outfits/{id}/feedback` — set feedback (`like`, `dislike`, `skip`, `none`)
  - `GET /outfits/history` — list outfits (most recent first)

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
  -d '{"category":"top","color":"navy"}'

# Request recommendation
curl -X POST http://127.0.0.1:8000/outfits/recommendation \
  -H "Authorization: Bearer $TOKEN"
```

## Database Notes
- Defaults to SQLite file `outfitguru.db` in the repo root.
- Change `OUTFITGURU_DATABASE_URL` for external DBs; run migrations accordingly (none included in MVP).

## Common Issues
- **Address already in use (8000):** stop existing uvicorn or change `--port`.
- **Wrong Python version:** install/use Python 3.12+ for compatibility.
- **Missing `pydantic-settings` or other deps:** ensure the virtualenv is active and `pip install -r requirements.txt` succeeded.

## Security
- Always set a strong `OUTFITGURU_SECRET_KEY`; rotate if exposed.
- Keep `.env` out of version control; only commit `.env.example`.
