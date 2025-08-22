from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    app_env: str = Field(default="development")

    secret_key: str = Field(default="change_me")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60)

    database_url: str = Field(default="sqlite+aiosqlite:///./hyperai.db")

    redis_url: str = Field(default="redis://localhost:6379/0")

    encryption_key: str = Field(default="")

    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_api_key: str | None = None

    backend_cors_origins: List[AnyHttpUrl] = Field(
        default_factory=lambda: [
            "http://localhost:8501",  # Streamlit default
            "http://localhost:3000",
        ]
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()