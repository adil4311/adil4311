from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header, HTTPException, Query, status

from backend.core.security import decode_token


async def get_current_user(authorization: Annotated[str | None, Header()]):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    return payload.get("sub")


Page = Annotated[int, Query(ge=1, le=1000, description="Page number")]
PageSize = Annotated[int, Query(ge=1, le=100, description="Items per page")]