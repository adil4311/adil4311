from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user
from backend.core.crypto import decrypt_string, encrypt_string
from backend.db.session import get_db
from backend.models.apikey import ApiKey


router = APIRouter(prefix="/settings", tags=["settings"])


class ApiKeyUpsert(BaseModel):
    provider: str
    key: str


class ApiKeyListItem(BaseModel):
    provider: str


@router.post("/api-keys", status_code=status.HTTP_204_NO_CONTENT)
async def upsert_api_key(
    data: ApiKeyUpsert,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> Response:
    provider = data.provider.lower()
    existing = await db.scalar(
        select(ApiKey).where(
            ApiKey.user_id == int(current_user), ApiKey.provider == provider
        )
    )
    if existing:
        existing.key_encrypted = encrypt_string(data.key)
    else:
        entry = ApiKey(
            user_id=int(current_user), provider=provider, key_encrypted=encrypt_string(data.key)
        )
        db.add(entry)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/api-keys", response_model=list[ApiKeyListItem])
async def list_api_keys(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> Any:
    result = await db.scalars(select(ApiKey).where(ApiKey.user_id == int(current_user)))
    return [ApiKeyListItem(provider=i.provider) for i in result.all()]