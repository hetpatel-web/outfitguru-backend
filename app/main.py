from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.routes import auth, outfits, users, wardrobe

settings = get_settings()

# Ensure models are imported so metadata is ready for table creation
from app import models  # noqa: E402,F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(wardrobe.router)
app.include_router(outfits.router)


@app.get("/", tags=["health"])
def read_root():
    return {"message": "OutfitGuru API is running"}
