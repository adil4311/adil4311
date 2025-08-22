from __future__ import annotations


from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..models import Project
from ..ai import ai_manager

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str
    description: str


class ProjectOut(BaseModel):
    id: str
    name: str
    description: str
    status: str

    class Config:
        from_attributes = True


@router.get("/", response_model=list[ProjectOut])
async def list_projects(db: AsyncSession = Depends(get_db)) -> list[ProjectOut]:
    # TODO: filter by current user when auth dependency is added
    result = await db.execute(select(Project).order_by(Project.created_at.desc()))
    projects = result.scalars().all()
    return [ProjectOut.model_validate(p) for p in projects]


@router.post("/", response_model=ProjectOut)
async def create_project(
    payload: ProjectCreate, db: AsyncSession = Depends(get_db)
) -> ProjectOut:
    project = Project(name=payload.name, description=payload.description)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return ProjectOut.model_validate(project)


class GenerateRequest(BaseModel):
    prompt: str
    model: str | None = None


@router.post("/{project_id}/generate")
async def generate_project_code(
    *,
    project_id: str = Path(...),
    payload: GenerateRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    # For MVP, call AI manager synchronously; later dispatch Celery task.
    code = await ai_manager.generate(payload.prompt, payload.model)
    project.generated_code = code
    project.status = "generated"
    await db.commit()
    return {"status": "generated"}


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: str, db: AsyncSession = Depends(get_db)
) -> ProjectOut:
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectOut.model_validate(project)