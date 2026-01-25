"""Department Model"""

from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.infrastructure.database.base import BaseModel


class Department(BaseModel):
    """Department model. Belongs to a clinic."""
    
    __tablename__ = "departments"
    
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    clinic_id = Column(UNIQUEIDENTIFIER, ForeignKey("clinics.id"), nullable=True, index=True)
    
    # Relationships (no employees table)
    clinic = relationship("Clinic", back_populates="departments")
    doctors = relationship("Doctor", back_populates="department")
    appointments = relationship("Appointment", back_populates="department")
