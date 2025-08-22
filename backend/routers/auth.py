from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import create_access_token, get_password_hash, verify_password
from ..db import get_db
from ..models import User

router = APIRouter()


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


async def _get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


@router.post("/signup", response_model=TokenResponse)
async def signup(payload: SignUpRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    existing = await _get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email exists")
    user = User(email=payload.email, password_hash=get_password_hash(payload.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(str(user.id), expires_minutes=60)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    user = await _get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid creds")
    token = create_access_token(str(user.id), expires_minutes=60)
    return TokenResponse(access_token=token)


@router.get("/me")
async def me() -> dict[str, str]:
    # For MVP, return static; later use JWT dependency
    return {"status": "ok"}