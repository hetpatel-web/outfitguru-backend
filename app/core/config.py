from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "OutfitGuru API"
    secret_key: str = Field("change-me", env="OUTFITGURU_SECRET_KEY")
    access_token_expire_minutes: int = 60 * 24  # 1 day
    algorithm: str = "HS256"
    database_url: str = Field("sqlite:///./outfitguru.db", env="OUTFITGURU_DATABASE_URL")
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
