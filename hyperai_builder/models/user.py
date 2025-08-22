"""
User model for HyperAI Builder.

Handles user authentication, profiles, and project management.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base

from ..core.logging import get_logger

logger = get_logger(__name__)


class User(Base):
    """User model for authentication and profile management."""
    
    __tablename__ = "users"
    
    # Authentication fields
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    salt: Mapped[str] = mapped_column(String(32), nullable=False)
    
    # Profile fields
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Account status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Subscription and limits
    subscription_tier: Mapped[str] = mapped_column(String(20), default="free", nullable=False)
    monthly_requests: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    requests_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reset_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # API keys (encrypted)
    openai_api_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    anthropic_api_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    google_api_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    
    def __init__(self, **kwargs: Any) -> None:
        """Initialize user with password hashing."""
        if 'password' in kwargs:
            password = kwargs.pop('password')
            self.set_password(password)
        super().__init__(**kwargs)
        
        # Set default reset date to next month
        if not self.reset_date:
            self.reset_date = datetime.now() + timedelta(days=30)
    
    def set_password(self, password: str) -> None:
        """Set and hash the user's password."""
        self.salt = secrets.token_hex(16)
        self.password_hash = self._hash_password(password, self.salt)
        logger.debug(f"Password set for user {self.username}")
    
    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        return self.password_hash == self._hash_password(password, self.salt)
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt using SHA-256."""
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def generate_api_token(self) -> str:
        """Generate a new API token for the user."""
        token = secrets.token_urlsafe(32)
        logger.info(f"Generated API token for user {self.username}")
        return token
    
    def can_make_request(self) -> bool:
        """Check if user can make a new request based on limits."""
        if self.is_premium:
            return True
        
        if datetime.now() >= self.reset_date:
            self.requests_used = 0
            self.reset_date = datetime.now() + timedelta(days=30)
            return True
        
        return self.requests_used < self.monthly_requests
    
    def increment_request_count(self) -> None:
        """Increment the request count for the user."""
        self.requests_used += 1
        logger.debug(f"Incremented request count for user {self.username}: {self.requests_used}")
    
    def get_full_name(self) -> str:
        """Get the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return self.username
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert user to dictionary, optionally including sensitive data."""
        data = super().to_dict()
        
        if not include_sensitive:
            # Remove sensitive fields
            data.pop('password_hash', None)
            data.pop('salt', None)
            data.pop('openai_api_key', None)
            data.pop('anthropic_api_key', None)
            data.pop('google_api_key', None)
        
        # Add computed fields
        data['full_name'] = self.get_full_name()
        data['can_make_request'] = self.can_make_request()
        
        return data
    
    @classmethod
    def get_by_email(cls, session, email: str):
        """Get user by email address."""
        return session.query(cls).filter(cls.email == email).first()
    
    @classmethod
    def get_by_username(cls, session, username: str):
        """Get user by username."""
        return session.query(cls).filter(cls.username == username).first()
    
    @classmethod
    def get_active_users(cls, session):
        """Get all active users."""
        return session.query(cls).filter(cls.is_active == True).all()


class UserSession(Base):
    """User session model for managing login sessions."""
    
    __tablename__ = "user_sessions"
    
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    session_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # IPv6 compatible
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __init__(self, **kwargs: Any) -> None:
        """Initialize session with default expiration."""
        if 'expires_at' not in kwargs:
            kwargs['expires_at'] = datetime.now() + timedelta(days=7)
        super().__init__(**kwargs)
    
    def is_expired(self) -> bool:
        """Check if the session has expired."""
        return datetime.now() > self.expires_at
    
    def extend_session(self, days: int = 7) -> None:
        """Extend the session expiration."""
        self.expires_at = datetime.now() + timedelta(days=days)
        logger.debug(f"Extended session for user {self.user_id}")
    
    @classmethod
    def get_valid_session(cls, session, token: str):
        """Get a valid session by token."""
        return session.query(cls).filter(
            cls.session_token == token,
            cls.is_active == True,
            cls.expires_at > datetime.now()
        ).first()
    
    @classmethod
    def cleanup_expired_sessions(cls, session) -> int:
        """Clean up expired sessions and return count of removed sessions."""
        expired_sessions = session.query(cls).filter(cls.expires_at <= datetime.now()).all()
        count = len(expired_sessions)
        
        for expired_session in expired_sessions:
            session.delete(expired_session)
        
        session.commit()
        logger.info(f"Cleaned up {count} expired sessions")
        return count


class APIKey(Base):
    """API key model for external service integrations."""
    
    __tablename__ = "api_keys"
    
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_type: Mapped[str] = mapped_column(String(20), nullable=False)  # openai, anthropic, google, custom
    encrypted_key: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    def increment_usage(self) -> None:
        """Increment usage count and update last used timestamp."""
        self.usage_count += 1
        self.last_used = datetime.now()
        logger.debug(f"Incremented usage for API key {self.name}")
    
    @classmethod
    def get_active_keys_by_type(cls, session, user_id: str, key_type: str):
        """Get active API keys of a specific type for a user."""
        return session.query(cls).filter(
            cls.user_id == user_id,
            cls.key_type == key_type,
            cls.is_active == True
        ).all()