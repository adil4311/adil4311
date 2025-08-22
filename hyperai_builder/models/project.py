"""
Project model for HyperAI Builder.

Handles project creation, code generation, and deployment tracking.
"""

import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base

from ..core.logging import get_logger

logger = get_logger(__name__)


class ProjectStatus(str, Enum):
    """Project status enumeration."""
    DRAFT = "draft"
    GENERATING = "generating"
    GENERATED = "generated"
    TESTING = "testing"
    TESTED = "tested"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ARCHIVED = "archived"


class ProjectType(str, Enum):
    """Project type enumeration."""
    WEB_APP = "web_app"
    MOBILE_APP = "mobile_app"
    API_SERVICE = "api_service"
    CHATBOT = "chatbot"
    DATA_ANALYZER = "data_analyzer"
    IMAGE_GENERATOR = "image_generator"
    AUTOMATION_TOOL = "automation_tool"
    CUSTOM = "custom"


class TechStack(str, Enum):
    """Technology stack enumeration."""
    PYTHON_FLASK = "python_flask"
    PYTHON_FASTAPI = "python_fastapi"
    PYTHON_DJANGO = "python_django"
    NODE_EXPRESS = "node_express"
    NODE_NEXTJS = "node_nextjs"
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    FLUTTER = "flutter"
    REACT_NATIVE = "react_native"
    PYTHON_STREAMLIT = "python_streamlit"
    PYTHON_GRADIO = "python_gradio"


class Project(Base):
    """Project model for AI-generated applications."""
    
    __tablename__ = "projects"
    
    # Basic information
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    project_type: Mapped[ProjectType] = mapped_column(String(50), nullable=False)
    tech_stack: Mapped[TechStack] = mapped_column(String(50), nullable=False)
    
    # Owner and collaborators
    owner_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    collaborators: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    # Project status and progress
    status: Mapped[ProjectStatus] = mapped_column(String(20), default=ProjectStatus.DRAFT, nullable=False)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-100
    
    # AI generation details
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    ai_model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    generation_cost: Mapped[Optional[float]] = mapped_column(String(20), nullable=True)
    generation_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # seconds
    
    # Generated code and files
    source_code: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    file_structure: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    dependencies: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Testing and deployment
    test_results: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    deployment_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    deployment_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    tags: Mapped[List[str]] = mapped_column(JSON, default=list)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_template: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    versions = relationship("ProjectVersion", back_populates="project", cascade="all, delete-orphan")
    deployments = relationship("ProjectDeployment", back_populates="project", cascade="all, delete-orphan")
    
    def __init__(self, **kwargs: Any) -> None:
        """Initialize project with default values."""
        super().__init__(**kwargs)
        if not self.tags:
            self.tags = []
        if not self.collaborators:
            self.collaborators = []
    
    def update_status(self, new_status: ProjectStatus, progress: Optional[int] = None) -> None:
        """Update project status and optionally progress."""
        old_status = self.status
        self.status = new_status
        if progress is not None:
            self.progress = progress
        
        logger.info(f"Project {self.name} status changed from {old_status} to {new_status}")
    
    def add_collaborator(self, user_id: str) -> None:
        """Add a collaborator to the project."""
        if user_id not in self.collaborators:
            self.collaborators.append(user_id)
            logger.info(f"Added collaborator {user_id} to project {self.name}")
    
    def remove_collaborator(self, user_id: str) -> None:
        """Remove a collaborator from the project."""
        if user_id in self.collaborators:
            self.collaborators.remove(user_id)
            logger.info(f"Removed collaborator {user_id} from project {self.name}")
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the project."""
        if tag not in self.tags:
            self.tags.append(tag)
            logger.debug(f"Added tag '{tag}' to project {self.name}")
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the project."""
        if tag in self.tags:
            self.tags.remove(tag)
            logger.debug(f"Removed tag '{tag}' from project {self.name}")
    
    def get_file_count(self) -> int:
        """Get the total number of files in the project."""
        if self.file_structure:
            return len(self.file_structure)
        return 0
    
    def get_total_lines(self) -> int:
        """Get the total number of lines of code."""
        if self.source_code:
            total_lines = 0
            for file_data in self.source_code.values():
                if isinstance(file_data, dict) and 'content' in file_data:
                    content = file_data['content']
                    if isinstance(content, str):
                        total_lines += len(content.split('\n'))
            return total_lines
        return 0
    
    def to_dict(self, include_code: bool = False) -> Dict[str, Any]:
        """Convert project to dictionary, optionally including source code."""
        data = super().to_dict()
        
        if not include_code:
            # Remove large code data for list views
            data.pop('source_code', None)
            data.pop('file_structure', None)
        
        # Add computed fields
        data['file_count'] = self.get_file_count()
        data['total_lines'] = self.get_total_lines()
        data['is_owner'] = True  # This should be set by the caller based on current user
        
        return data
    
    @classmethod
    def get_by_owner(cls, session, owner_id: str, limit: Optional[int] = None):
        """Get projects by owner."""
        query = session.query(cls).filter(cls.owner_id == owner_id)
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @classmethod
    def get_public_templates(cls, session, limit: Optional[int] = None):
        """Get public template projects."""
        query = session.query(cls).filter(
            cls.is_template == True,
            cls.is_public == True
        )
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @classmethod
    def search_projects(cls, session, query: str, limit: Optional[int] = None):
        """Search projects by name, description, or tags."""
        search_query = f"%{query}%"
        db_query = session.query(cls).filter(
            (cls.name.ilike(search_query)) |
            (cls.description.ilike(search_query)) |
            (cls.tags.any(lambda tag: query.lower() in tag.lower()))
        )
        if limit:
            db_query = db_query.limit(limit)
        return db_query.all()


class ProjectVersion(Base):
    """Project version model for tracking changes."""
    
    __tablename__ = "project_versions"
    
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    version_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Version data
    source_code: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    file_structure: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False)
    dependencies: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    # Change tracking
    changes_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="versions")
    
    def __init__(self, **kwargs: Any) -> None:
        """Initialize version with default values."""
        super().__init__(**kwargs)
        if not self.version_name:
            self.version_name = f"v{self.version_number}"
    
    @classmethod
    def get_latest_version(cls, session, project_id: str):
        """Get the latest version of a project."""
        return session.query(cls).filter(
            cls.project_id == project_id
        ).order_by(cls.version_number.desc()).first()
    
    @classmethod
    def get_version(cls, session, project_id: str, version_number: int):
        """Get a specific version of a project."""
        return session.query(cls).filter(
            cls.project_id == project_id,
            cls.version_number == version_number
        ).first()


class ProjectDeployment(Base):
    """Project deployment model for tracking deployments."""
    
    __tablename__ = "project_deployments"
    
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    deployment_type: Mapped[str] = mapped_column(String(50), nullable=False)  # vercel, heroku, aws, etc.
    
    # Deployment details
    deployment_url: Mapped[str] = mapped_column(String(500), nullable=False)
    deployment_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    
    # Configuration and logs
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    logs: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="deployments")
    
    def __init__(self, **kwargs: Any) -> None:
        """Initialize deployment with default values."""
        super().__init__(**kwargs)
        if not self.logs:
            self.logs = []
    
    def add_log(self, message: str) -> None:
        """Add a log message to the deployment."""
        timestamp = datetime.now().isoformat()
        self.logs.append(f"[{timestamp}] {message}")
        logger.debug(f"Added deployment log: {message}")
    
    def update_status(self, new_status: str, error_message: Optional[str] = None) -> None:
        """Update deployment status."""
        old_status = self.status
        self.status = new_status
        if error_message:
            self.error_message = error_message
        
        logger.info(f"Deployment {self.deployment_id} status changed from {old_status} to {new_status}")
    
    @classmethod
    def get_active_deployments(cls, session, project_id: str):
        """Get active deployments for a project."""
        return session.query(cls).filter(
            cls.project_id == project_id,
            cls.status.in_(["pending", "deploying", "deployed"])
        ).all()