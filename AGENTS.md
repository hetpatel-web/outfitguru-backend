# OutfitGuru Backend — Agent Notes

## Branch policy
- Default branch: `main`; `dev` exists as an integration branch.
- Direct pushes/force pushes to `main` are blocked by policy and local hook.
- Always open a PR into `main` (or `dev` → `main`).

## Required checks for merges into `main`
- GitHub Actions workflow: `.github/workflows/backend.yml`
- Status check name: `backend-tests` (runs pytest with SQLite in-memory DB)

## Local safeguards
- A pre-push hook blocks pushing `main`: `.githooks/pre-push`
- Ensure hooks are active after clone: `git config core.hooksPath .githooks`

## PR expectations
- Target `main` (or `dev` if integrating feature branches).
- CI must pass (`backend-tests`).
- Keep branch up to date before merge; resolve review conversations.

## Quick commands
- Run tests locally: `pytest -q`
- Verify hook: attempt `git push origin main` (should be blocked on `main`)
