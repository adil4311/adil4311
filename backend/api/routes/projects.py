from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user
from backend.db.session import get_db
from backend.models.project import Project
from backend.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate


router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=list[ProjectRead])
async def list_projects(
    db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_user)
) -> Any:
    result = await db.scalars(select(Project).where(Project.owner_id == int(current_user)))
    return [ProjectRead.model_validate(p) for p in result.all()]


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> Any:
    project = Project(owner_id=int(current_user), **data.model_dump())
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return ProjectRead.model_validate(project)


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> Any:
    project = await db.get(Project, project_id)
    if not project or project.owner_id != int(current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return ProjectRead.model_validate(project)


@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> Any:
    project = await db.get(Project, project_id)
    if not project or project.owner_id != int(current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(project, k, v)
    await db.commit()
    await db.refresh(project)
    return ProjectRead.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> Response:
    project = await db.get(Project, project_id)
    if not project or project.owner_id != int(current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    await db.delete(project)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)