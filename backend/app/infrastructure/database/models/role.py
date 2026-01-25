"""Role Model"""

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.infrastructure.database.base import BaseModel


class Role(BaseModel):
    """Role model for authorization. User–role link is via linked_clinics (UserClinicRole), not user_roles."""
    
    __tablename__ = "roles"
    
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    
    user_clinic_assignments = relationship("UserClinicRole", back_populates="role")
