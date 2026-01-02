# Staging Notes

- Backend: https://outfitguru-backend.onrender.com
- Health: `GET /health` (JSON `{"status":"ok"}`)
- Docs: https://outfitguru-backend.onrender.com/docs
- Frontend (Cloudflare Pages): use the current Pages URL/custom domain configured in Cloudflare.

## Behavior and limitations
- Free-tier cold starts on Render may add first-request latency.
- Render free instances can sleep when idle; expect brief warm-up on next request.
- Token auth: JWT expires in ~24h (see `access_token_expire_minutes`); clients should re-login after expiry.
- CORS: allow-list includes the Pages domain(s) and localhost:5173 for dev; update `OUTFITGURU_CORS_ORIGINS` when domains change.
- Database: Neon Postgres in staging; local dev uses SQLite.

## Logging
- Each request logs: method, path, status code, duration (ms). Unhandled exceptions are logged server-side and return a JSON 500.

## Verification checklist
- `GET /health` returns 200 with `{"status":"ok"}`.
- `GET /docs` loads Swagger UI.
- End-to-end via frontend: register/login → add 3 items (top/bottom/footwear) → generate recommendation → submit feedback → see history updated.
- Review Render logs: requests are logged with status/duration; no unhandled exceptions.
