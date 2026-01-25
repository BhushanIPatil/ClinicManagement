"""User Model"""

from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.infrastructure.database.base import BaseModel


class User(BaseModel):
    """User model for authentication and authorization.
    Roles come from clinic_role_assignments (linked_clinics) only; no user_roles or employees table.
    """
    
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Roles are via linked_clinics (UserClinicRole), not user_roles
    clinic_role_assignments = relationship("UserClinicRole", back_populates="user")
