from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "OutfitGuru API"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60 * 24  # 1 day
    algorithm: str = "HS256"
    database_url: str = "sqlite:///./outfitguru.db"
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_prefix="OUTFITGURU_",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
