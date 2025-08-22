from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user
from backend.core.crypto import decrypt_string
from backend.db.session import get_db
from backend.models.apikey import ApiKey
from backend.models.project import Project
from backend.services.orchestrator import OrchestratorService


router = APIRouter(prefix="/ai", tags=["ai"])


class BlueprintRequest(BaseModel):
    description: str
    project_id: int | None = None
    provider: str | None = None


class BlueprintResponse(BaseModel):
    blueprint_markdown: str


@router.post("/blueprint", response_model=BlueprintResponse)
async def generate_blueprint(
    request: BlueprintRequest,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> Any:
    provider = (request.provider or "openai").lower()
    api_key: str | None = None
    key_row = await db.scalar(
        select(ApiKey).where(ApiKey.user_id == int(current_user), ApiKey.provider == provider)
    )
    if key_row:
        api_key = decrypt_string(key_row.key_encrypted)
    orchestrator = OrchestratorService()
    md = await orchestrator.generate_blueprint(
        description=request.description, provider=provider, api_key=api_key
    )
    if request.project_id:
        project = await db.get(Project, request.project_id)
        if project and project.owner_id == int(current_user):
            project.blueprint_markdown = md
            await db.commit()
    return BlueprintResponse(blueprint_markdown=md)


class CodeGenRequest(BaseModel):
    project_id: int
    provider: str | None = None
    refine_message: str | None = None


class CodeGenResponse(BaseModel):
    status: str


@router.post("/generate", response_model=CodeGenResponse)
async def generate_code(
    request: CodeGenRequest,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> Any:
    from celery_app import celery_app

    provider = (request.provider or "openai").lower()
    project = await db.get(Project, request.project_id)
    if not project or project.owner_id != int(current_user):
        return CodeGenResponse(status="not_found")
    celery_app.send_task(
        "generate_code_scaffold",
        kwargs={"description": project.description, "provider": provider},
    )
    return CodeGenResponse(status="queued")