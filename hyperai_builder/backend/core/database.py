"""
Database connection and session management for HyperAI Builder.

Handles database initialization, connection pooling, and session management.
"""

import asyncio
from contextlib import contextmanager
from typing import AsyncGenerator, Generator, Optional

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from ...core.config import get_database_url, get_settings
from ...core.logging import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Database connection and session manager."""
    
    def __init__(self):
        """Initialize database manager."""
        self.settings = get_settings()
        self.engine: Optional[Engine] = None
        self.async_engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[sessionmaker] = None
        self.async_session_factory: Optional[sessionmaker] = None
        
        # Initialize database
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize database connection and session factory."""
        database_url = get_database_url()
        
        # Determine if using async or sync
        is_async = database_url.startswith(("postgresql+asyncpg://", "mysql+asyncmy://"))
        
        if is_async:
            self._init_async_database(database_url)
        else:
            self._init_sync_database(database_url)
    
    def _init_sync_database(self, database_url: str) -> None:
        """Initialize synchronous database connection."""
        # Configure engine based on database type
        if database_url.startswith("sqlite"):
            # SQLite configuration
            engine_kwargs = {
                "url": database_url,
                "echo": self.settings.database.echo,
                "poolclass": NullPool,  # SQLite doesn't support connection pooling
                "connect_args": {"check_same_thread": False}
            }
        else:
            # PostgreSQL/MySQL configuration
            engine_kwargs = {
                "url": database_url,
                "echo": self.settings.database.echo,
                "pool_size": self.settings.database.pool_size,
                "max_overflow": self.settings.database.max_overflow,
                "pool_pre_ping": True,
                "pool_recycle": 3600,  # Recycle connections every hour
            }
        
        # Create engine
        self.engine = create_engine(**engine_kwargs)
        
        # Configure session factory
        self.session_factory = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
        
        # Add engine event listeners
        self._add_engine_events(self.engine)
        
        logger.info(f"Initialized synchronous database: {database_url}")
    
    def _init_async_database(self, database_url: str) -> None:
        """Initialize asynchronous database connection."""
        # Create async engine
        self.async_engine = create_async_engine(
            database_url,
            echo=self.settings.database.echo,
            pool_size=self.settings.database.pool_size,
            max_overflow=self.settings.database.max_overflow,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        
        # Configure async session factory
        self.async_session_factory = sessionmaker(
            bind=self.async_engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
        
        logger.info(f"Initialized asynchronous database: {database_url}")
    
    def _add_engine_events(self, engine: Engine) -> None:
        """Add engine event listeners for monitoring and debugging."""
        
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set SQLite pragmas for better performance."""
            if engine.url.drivername == "sqlite":
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA cache_size=10000")
                cursor.execute("PRAGMA temp_store=MEMORY")
                cursor.close()
        
        @event.listens_for(engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Log connection checkout."""
            logger.debug("Database connection checked out")
        
        @event.listens_for(engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """Log connection checkin."""
            logger.debug("Database connection checked in")
    
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session."""
        if not self.session_factory:
            raise RuntimeError("Database not initialized")
        
        session = self.session_factory()
        try:
            yield session
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            session.close()
    
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an asynchronous database session."""
        if not self.async_session_factory:
            raise RuntimeError("Async database not initialized")
        
        async with self.async_session_factory() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                logger.error(f"Async database session error: {str(e)}")
                raise
    
    @contextmanager
    def get_session_context(self) -> Generator[Session, None, None]:
        """Get a database session as a context manager."""
        if not self.session_factory:
            raise RuntimeError("Database not initialized")
        
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_session_context() as session:
                session.execute(text("SELECT 1"))
                logger.info("Database connection test successful")
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False
    
    async def test_async_connection(self) -> bool:
        """Test asynchronous database connection."""
        try:
            async with self.get_async_session() as session:
                await session.execute(text("SELECT 1"))
                logger.info("Async database connection test successful")
                return True
        except Exception as e:
            logger.error(f"Async database connection test failed: {str(e)}")
            return False
    
    def close(self) -> None:
        """Close database connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("Synchronous database engine disposed")
        
        if self.async_engine:
            asyncio.create_task(self.async_engine.dispose())
            logger.info("Asynchronous database engine disposal scheduled")
    
    def get_engine_info(self) -> dict:
        """Get database engine information."""
        info = {
            "database_type": "unknown",
            "is_async": False,
            "pool_size": 0,
            "max_overflow": 0,
        }
        
        if self.engine:
            info["database_type"] = self.engine.url.drivername
            info["is_async"] = False
            if hasattr(self.engine, 'pool'):
                info["pool_size"] = self.engine.pool.size()
                info["max_overflow"] = self.engine.pool.overflow()
        
        if self.async_engine:
            info["database_type"] = self.async_engine.url.drivername
            info["is_async"] = True
            if hasattr(self.async_engine, 'pool'):
                info["pool_size"] = self.async_engine.pool.size()
                info["max_overflow"] = self.async_engine.pool.overflow()
        
        return info


# Global database manager instance
db_manager = DatabaseManager()


def get_db() -> Generator[Session, None, None]:
    """Dependency function to get database session."""
    yield from db_manager.get_session()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency function to get asynchronous database session."""
    async for session in db_manager.get_async_session():
        yield session


def get_db_context():
    """Dependency function to get database session context."""
    return db_manager.get_session_context()


# Database initialization functions
def init_database() -> None:
    """Initialize database tables."""
    from ...models.base import Base
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=db_manager.engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise


def drop_database() -> None:
    """Drop all database tables."""
    from ...models.base import Base
    
    try:
        # Drop all tables
        Base.metadata.drop_all(bind=db_manager.engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {str(e)}")
        raise


def reset_database() -> None:
    """Reset database by dropping and recreating all tables."""
    try:
        drop_database()
        init_database()
        logger.info("Database reset successfully")
    except Exception as e:
        logger.error(f"Failed to reset database: {str(e)}")
        raise