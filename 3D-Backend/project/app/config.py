"""Centralized application settings loaded from environment variables / .env file."""

from typing import List, Union

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # General
    APP_NAME: str = "AI Virtual Dressing Room"
    API_V1_PREFIX: str = "/api"

    # CORS — accept a comma-separated list of origins in .env
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = []

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/dressing_room"

    # JWT auth
    SECRET_KEY: str = "change-me-to-a-long-random-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # File uploads
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_IMAGE_TYPES: Union[str, List[str]] = "image/jpeg,image/png,image/webp"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors(cls, v):
        if isinstance(v, str):
            # Allow empty string -> no origins
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("ALLOWED_IMAGE_TYPES", mode="before")
    @classmethod
    def _split_types(cls, v):
        if isinstance(v, str):
            return [t.strip() for t in v.split(",") if t.strip()]
        return v

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


settings = Settings()
