from __future__ import annotations

import base64
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

from backend.core.config import get_settings


@lru_cache(maxsize=1)
def get_fernet() -> Fernet:
    settings = get_settings()
    key = settings.fernet_secret_key
    if not key:
        raise RuntimeError("FERNET_SECRET_KEY not configured")
    if isinstance(key, str):
        key_bytes = key.encode()
    else:
        key_bytes = key
    # Validate key
    try:
        base64.urlsafe_b64decode(key_bytes)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("Invalid FERNET_SECRET_KEY") from exc
    return Fernet(key_bytes)


def encrypt_string(value: str) -> str:
    token = get_fernet().encrypt(value.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_string(token: str) -> str:
    try:
        value = get_fernet().decrypt(token.encode("utf-8"))
    except InvalidToken as exc:
        raise RuntimeError("Failed to decrypt value") from exc
    return value.decode("utf-8")