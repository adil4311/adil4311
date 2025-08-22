from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Uses pydantic-settings to map env vars to strongly-typed fields.
    """

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    # Core
    environment: str = Field(default="local")
    debug: bool = Field(default=True)
    secret_key: str = Field(default="change_me")
    access_token_expire_minutes: int = Field(default=30)
    jwt_algorithm: str = Field(default="HS256")

    # Database
    database_url: str = Field(default="sqlite+aiosqlite:///./dev.db")

    # Redis / Celery
    redis_broker_url: str = Field(default="redis://localhost:6379/0")
    redis_result_backend: str = Field(default="redis://localhost:6379/1")

    # CORS
    backend_cors_origins: List[AnyHttpUrl] | List[str] = Field(
        default_factory=lambda: [
            "http://localhost",
            "http://localhost:3000",
            "http://localhost:8501",
        ]
    )

    # Encryption
    fernet_secret_key: str = Field(default="")

    # AI Providers
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")

    # Telemetry / Monitoring
    sentry_dsn: str = Field(default="")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()  # type: ignore[call-arg]