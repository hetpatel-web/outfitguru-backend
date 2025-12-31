# OutfitGuru Backend (MVP)
FastAPI + SQLite backend for recommending outfits from a user's wardrobe. Focused on clarity, explainability, and user control.

## Quickstart
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at http://127.0.0.1:8000 with docs at http://127.0.0.1:8000/docs.

### Configuration
- `OUTFITGURU_SECRET_KEY` (required in production; defaults to `change-me` for local)
- `OUTFITGURU_DATABASE_URL` (defaults to `sqlite:///./outfitguru.db`)
- CORS allows `http://localhost:5173` by default for the Vite frontend.

## Key Endpoints
- `POST /auth/register` — `{email, password}` → returns user + token
- `POST /auth/login` — `{email, password}` → returns token
- `GET /me` — current user (requires Bearer token)
- `POST /wardrobe/items` — create clothing item (requires token)
- `GET /wardrobe/items` — list clothing items (requires token)
- `POST /outfits/recommendation` — rule-based outfit for today; persists result (requires token)
- `POST /outfits/{outfit_id}/feedback` — set feedback (like/dislike/skip/none)
- `GET /outfits/history` — list outfits (most recent first)

## cURL Examples
```bash
# Register
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"secret123"}'

# Login (get token)
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"secret123"}'
# Save the access_token from the response to use below:
TOKEN="paste-token-here"

# Add wardrobe items
curl -X POST http://127.0.0.1:8000/wardrobe/items \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"category":"top","color":"navy"}'

curl -X POST http://127.0.0.1:8000/wardrobe/items \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"category":"bottom","color":"black"}'

curl -X POST http://127.0.0.1:8000/wardrobe/items \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"category":"footwear","color":"white"}'

# Get an outfit recommendation
curl -X POST http://127.0.0.1:8000/outfits/recommendation \
  -H "Authorization: Bearer $TOKEN"

# Provide feedback on an outfit
curl -X POST http://127.0.0.1:8000/outfits/1/feedback \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"feedback":"like"}'

# View history
curl -X GET http://127.0.0.1:8000/outfits/history \
  -H "Authorization: Bearer $TOKEN"
```
