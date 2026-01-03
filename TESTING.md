# Testing

## Backend
- Local: `cd outfitguru-backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && pytest`
- CI: `.github/workflows/backend.yml` runs `pytest` with `OUTFITGURU_DATABASE_URL=sqlite:///:memory:`.
- Env vars: tests default to SQLite; no external DB required.

Key flows covered:
- Auth + wardrobe + recommendation happy paths
- Feedback persistence
- History ordering (newest first)
- Recommendation rules (avoid repeat when alternatives exist, include reason)

## Frontend
- Local: `cd outfitguru-frontend && npm install && npm run build`
- CI: `.github/workflows/frontend.yml` uses Node from `.nvmrc`, runs `npm ci` and `npm run build`.

Notes:
- Keep tests fast and deterministic; no external services are called.
