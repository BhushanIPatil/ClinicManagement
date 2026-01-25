"""
Base Model Module

This module defines the base database model class with common functionality:
- UUID primary keys
- Automatic timestamps (created_at, updated_at)
- Soft delete support
- Common query methods

All domain models should inherit from BaseModel instead of Base directly.
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, DateTime, Boolean, String
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr
from sqlalchemy.sql import func

# Create declarative base
Base = declarative_base()


class BaseModel(Base):
    """
    Base Model Class
    
    All database models should inherit from this class to get:
    - UUID primary key
    - Automatic timestamps
    - Soft delete functionality
    - Common query methods
    
    Attributes:
        id: UUID primary key
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
        deleted_at: Timestamp when record was soft deleted (None if not deleted)
        is_deleted: Boolean flag for soft delete status
    
    Example:
        class Patient(BaseModel):
            __tablename__ = "patients"
            
            name = Column(String(255), nullable=False)
            email = Column(String(255), unique=True, nullable=False)
    """
    
    __abstract__ = True  # This is an abstract base class
    
    # UUID Primary Key
    # Using UNIQUEIDENTIFIER for SQL Server compatibility
    id = Column(
        UNIQUEIDENTIFIER,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        index=True,
        comment="Primary key UUID"
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="Timestamp when record was created"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when record was last updated"
    )
    
    # Soft Delete Support
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        index=True,
        comment="Timestamp when record was soft deleted"
    )
    
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Boolean flag for soft delete status"
    )
    
    @declared_attr
    def __tablename__(cls) -> str:
        """
        Automatically generate table name from class name.
        
        Converts PascalCase to snake_case and pluralizes.
        Example: Patient -> patients, AppointmentRecord -> appointment_records
        
        Returns:
            str: Table name in snake_case, pluralized
        """
        # Convert PascalCase to snake_case
        import re
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        # Simple pluralization (can be enhanced)
        if not name.endswith('s'):
            name += 's'
        return name
    
    def soft_delete(self):
        """
        Soft delete this record.
        
        Sets is_deleted to True and deleted_at to current timestamp.
        The record remains in the database but is excluded from normal queries.
        """
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """
        Restore a soft-deleted record.
        
        Sets is_deleted to False and clears deleted_at.
        """
        self.is_deleted = False
        self.deleted_at = None
    
    def is_active(self) -> bool:
        """
        Check if the record is active (not soft deleted).
        
        Returns:
            bool: True if record is active, False if soft deleted
        """
        return not self.is_deleted
    
    def __repr__(self) -> str:
        """
        String representation of the model.
        
        Returns:
            str: String representation
        """
        return f"<{self.__class__.__name__}(id={self.id}, is_deleted={self.is_deleted})>"
    
    @classmethod
    def get_active_query(cls, session):
        """
        Get a query that excludes soft-deleted records.
        
        This is a helper method for repositories to easily filter out
        soft-deleted records.
        
        Args:
            session: SQLAlchemy session
            
        Returns:
            Query: Query object filtered to active records only
        """
        from sqlalchemy.orm import Query
        return session.query(cls).filter(cls.is_deleted == False)
    
    @classmethod
    def get_all_query(cls, session, include_deleted: bool = False):
        """
        Get a query that optionally includes soft-deleted records.
        
        Args:
            session: SQLAlchemy session
            include_deleted: If True, include soft-deleted records
            
        Returns:
            Query: Query object
        """
        from sqlalchemy.orm import Query
        query = session.query(cls)
        if not include_deleted:
            query = query.filter(cls.is_deleted == False)
        return query
