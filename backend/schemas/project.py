from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    blueprint_markdown: Optional[str] = None
    code_repo_url: Optional[str] = None


class ProjectRead(ProjectBase):
    id: int
    owner_id: int
    blueprint_markdown: Optional[str] = None
    code_repo_url: Optional[str] = None

    class Config:
        from_attributes = True