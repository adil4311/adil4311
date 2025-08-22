"""
Base database model for HyperAI Builder.

Provides common fields and methods for all database models.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

from ..core.logging import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models."""
    
    # Common fields
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update model from dictionary."""
        for key, value in data.items():
            if hasattr(self, key) and key not in ['id', 'created_at', 'updated_at']:
                setattr(self, key, value)
                logger.debug(f"Updated {key} to {value}")
    
    @classmethod
    def get_by_id(cls, session, model_id: str):
        """Get model by ID."""
        return session.query(cls).filter(cls.id == model_id).first()
    
    @classmethod
    def get_all(cls, session, limit: Optional[int] = None, offset: Optional[int] = None):
        """Get all models with optional pagination."""
        query = session.query(cls)
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def save(self, session) -> None:
        """Save the model to the database."""
        try:
            session.add(self)
            session.commit()
            logger.info(f"Saved {self.__class__.__name__} with ID {self.id}")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save {self.__class__.__name__}: {str(e)}")
            raise
    
    def delete(self, session) -> None:
        """Delete the model from the database."""
        try:
            session.delete(self)
            session.commit()
            logger.info(f"Deleted {self.__class__.__name__} with ID {self.id}")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete {self.__class__.__name__}: {str(e)}")
            raise


# Legacy support for SQLAlchemy 1.x style
BaseLegacy = declarative_base()


class BaseModelLegacy(BaseLegacy):
    """Legacy base model for backward compatibility."""
    
    __abstract__ = True
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result