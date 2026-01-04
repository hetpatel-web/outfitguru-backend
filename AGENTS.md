# OutfitGuru Backend — AGENTS

## 1) Project Context
- OutfitGuru: calm personal AI stylist using the user’s wardrobe; deterministic, explainable, text-first; no social/shopping/trend pressure.
- This repo: FastAPI + SQLAlchemy API for auth, wardrobe CRUD, deterministic recommendations, calendar/feedback/history.

## 2) Safety & Workflow Rules
- Branches: default `main`; `dev` is integration. Never commit directly to `main`; use feature branches → PR into `dev`/`main`.
- CI: `.github/workflows/backend.yml` check `backend-tests` must pass; keep branch up to date; resolve conversations.
- Local hook blocks pushing `main`: `.githooks/pre-push`; ensure `git config core.hooksPath .githooks`.
- Scope: do not change CI/branch rules or add deps without approval; no social/shopping/trend features; logic stays deterministic/explainable.
- API changes must update `api-contract.md` (monorepo) and keep request/response types stable.

## 3) Quickstart Commands
- Install: `python3.12 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Run dev: `uvicorn app.main:app --reload --port 8000`
- Test: `source .venv/bin/activate && pytest -q`
- Lint/format: none enforced; keep imports tidy.
- Env: copy `.env.example` → `.env`; set `OUTFITGURU_SECRET_KEY`; optional `OUTFITGURU_DATABASE_URL`.

## 4) Repo Map
- `app/main.py` (FastAPI app + routers), `app/routes/*` (auth, wardrobe, outfits, calendar).
- `app/models/*`, `app/schemas/*`, `app/services/*` (catalog, recommender, calendar), `app/db/*` (session, migrations helper).
- `tests/` (API + rules); API contract lives in monorepo root.

## 5) Architecture Notes
- Flow: request → router → deps (auth/session) → services → models/DB. SQLite by default; Postgres via `OUTFITGURU_DATABASE_URL`.
- Recommender is rule-based/deterministic; keep explanations intact and predictable; handle `need_more_items`.
- Migrations: extend `app/db/migrations.py` when schema changes; avoid ad-hoc DB drift.
- Do not change auth/token rules or wardrobe catalog shapes without updating schemas/tests/contract.

## 6) Common Tasks (Recipes)
- Add endpoint: update router + schema + service; add tests in `tests/`; update `api-contract.md`.
- Change schema/model: adjust model + Pydantic schema + migrations helper; add/adjust tests.
- Update recommendation logic: preserve determinism and `need_more_items`; add tests in `tests/test_rules.py`.

## 7) Definition of Done
- `pytest -q` passes; `backend-tests` green in CI.
- API contract updated for any request/response change; migrations covered.
- No new deps unless justified; docs (README/AGENTS) updated if behavior shifts.

## 8) PR Checklist
- On a feature branch; branch up to date with `main`/`dev`.
- `pytest -q` run locally; `backend-tests` expected to pass.
- Contract/migrations updated if applicable; conversations resolved.
- Hooks active (`core.hooksPath .githooks`); no direct pushes to `main`.
