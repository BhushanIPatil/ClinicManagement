"""
Database Module

This module handles database connection and session management.
Provides FastAPI-compatible dependency injection for database sessions.
"""

from typing import Generator
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine

from app.core.config import settings


class DatabaseManager:
    """Database Manager for handling connections."""
    
    def __init__(self):
        self.sync_engine = None
        self.sync_session_factory = None
    
    def initialize(self):
        """Initialize database engine and session factory."""
        self.sync_engine = create_engine(
            settings.database_url,
            echo=settings.DB_ECHO,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_pre_ping=settings.DB_POOL_PRE_PING,
        )
        
        self.sync_session_factory = sessionmaker(
            bind=self.sync_engine,
            autocommit=False,
            autoflush=False,
        )
    
    async def close(self):
        """Close all database connections."""
        if self.sync_engine:
            self.sync_engine.dispose()
    
    def get_session(self) -> Session:
        """Get a new database session (direct call, no context manager)."""
        if not self.sync_session_factory:
            raise RuntimeError("Database not initialized")
        return self.sync_session_factory()


# Global database manager instance
db_manager = DatabaseManager()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.
    
    This is a plain generator function (NOT decorated with @contextmanager).
    FastAPI handles the generator protocol directly.
    
    Usage:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            # Use db session
            pass
    
    Yields:
        Session: Database session
    """
    if not db_manager.sync_session_factory:
        raise RuntimeError("Database not initialized. Call db_manager.initialize() first.")
    
    db = db_manager.sync_session_factory()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
