"""
Configuration management for HyperAI Builder.

Handles environment variables, settings validation, and configuration
for different environments (development, production, testing).
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseSettings, Field, validator


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    url: str = Field(default="sqlite:///./hyperai_builder.db")
    echo: bool = Field(default=False)
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)
    
    @validator("url")
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        if not v.startswith(("sqlite://", "postgresql://", "mysql://")):
            raise ValueError("Invalid database URL format")
        return v


class RedisSettings(BaseSettings):
    """Redis configuration settings."""
    
    url: str = Field(default="redis://localhost:6379")
    password: Optional[str] = None
    db: int = Field(default=0)
    max_connections: int = Field(default=20)


class SecuritySettings(BaseSettings):
    """Security configuration settings."""
    
    secret_key: str = Field(..., description="Secret key for JWT tokens")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)
    
    @validator("secret_key")
    def validate_secret_key(cls, v: str) -> str:
        """Ensure secret key is sufficiently long."""
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v


class AISettings(BaseSettings):
    """AI model configuration settings."""
    
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    
    # Model configurations
    default_model: str = Field(default="gpt-4o")
    max_tokens: int = Field(default=4000)
    temperature: float = Field(default=0.7)
    
    # Rate limiting
    requests_per_minute: int = Field(default=60)
    max_concurrent_requests: int = Field(default=10)


class UISettings(BaseSettings):
    """UI configuration settings."""
    
    theme: str = Field(default="dark")
    primary_color: str = Field(default="#6366f1")
    accent_color: str = Field(default="#8b5cf6")
    font_family: str = Field(default="Roboto, sans-serif")
    
    # Animation settings
    enable_animations: bool = Field(default=True)
    animation_duration: float = Field(default=0.3)
    
    # Responsive breakpoints
    mobile_breakpoint: int = Field(default=768)
    tablet_breakpoint: int = Field(default=1024)


class Settings(BaseSettings):
    """Main application settings."""
    
    # Application
    app_name: str = Field(default="HyperAI Builder")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    environment: str = Field(default="development")
    
    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    reload: bool = Field(default=True)
    
    # Database
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    
    # Redis
    redis: RedisSettings = Field(default_factory=RedisSettings)
    
    # Security
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    
    # AI
    ai: AISettings = Field(default_factory=AISettings)
    
    # UI
    ui: UISettings = Field(default_factory=UISettings)
    
    # Paths
    base_dir: Path = Field(default=Path(__file__).parent.parent.parent)
    static_dir: Path = Field(default=Path(__file__).parent.parent.parent / "static")
    templates_dir: Path = Field(default=Path(__file__).parent.parent.parent / "templates")
    
    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_nested_delimiter = "__"


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


def get_database_url() -> str:
    """Get database URL from environment or settings."""
    return os.getenv("DATABASE_URL", get_settings().database.url)


def get_redis_url() -> str:
    """Get Redis URL from environment or settings."""
    return os.getenv("REDIS_URL", get_settings().redis.url)


def get_secret_key() -> str:
    """Get secret key from environment or settings."""
    return os.getenv("SECRET_KEY", get_settings().security.secret_key)


# Environment-specific settings
def is_development() -> bool:
    """Check if running in development environment."""
    return get_settings().environment.lower() == "development"


def is_production() -> bool:
    """Check if running in production environment."""
    return get_settings().environment.lower() == "production"


def is_testing() -> bool:
    """Check if running in testing environment."""
    return get_settings().environment.lower() == "testing"