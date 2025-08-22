from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt
from cryptography.fernet import Fernet, InvalidToken
from loguru import logger
from passlib.context import CryptContext

from ..core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    expire_delta = timedelta(minutes=expires_minutes or settings.access_token_expire_minutes)
    expire = datetime.now(tz=timezone.utc) + expire_delta
    to_encode: Dict[str, Any] = {"sub": subject, "exp": expire}
    token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)
    return token


def _get_fernet() -> Fernet | None:
    key = settings.encryption_key
    if not key:
        logger.warning("ENCRYPTION_KEY not set; secrets won't be encrypted at rest")
        return None
    try:
        return Fernet(key)
    except Exception as exc:  # noqa: BLE001
        logger.error("Invalid ENCRYPTION_KEY: {}", exc)
        return None


def encrypt_secret(value: str) -> str:
    f = _get_fernet()
    if not f:
        return value
    return f.encrypt(value.encode()).decode()


def decrypt_secret(value: str) -> str:
    f = _get_fernet()
    if not f:
        return value
    try:
        return f.decrypt(value.encode()).decode()
    except InvalidToken:
        logger.error("Failed to decrypt secret; returning raw value")
        return value