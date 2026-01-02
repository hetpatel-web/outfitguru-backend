import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.routes import auth, outfits, users, wardrobe

settings = get_settings()

# Ensure models are imported so metadata is ready for table creation
from app import models  # noqa: E402,F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

logger = logging.getLogger("outfitguru")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unhandled exception during request")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    duration_ms = (time.perf_counter() - start) * 1000
    logger.info("%s %s -> %s (%.1f ms)", request.method, request.url.path, response.status_code, duration_ms)
    return response

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(wardrobe.router)
app.include_router(outfits.router)


@app.get("/", tags=["health"])
def read_root():
    return {"message": "OutfitGuru API is running"}


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
