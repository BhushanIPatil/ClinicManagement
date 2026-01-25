"""Doctor Model"""

from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.infrastructure.database.base import BaseModel


class Doctor(BaseModel):
    """Doctor model."""
    
    __tablename__ = "doctors"
    
    doctor_number = Column(String(20), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    specialization = Column(String(100), nullable=True)
    license_number = Column(String(50), unique=True, nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    is_available = Column(Boolean, default=True, nullable=False)
    
    # Foreign Keys
    user_id = Column(UNIQUEIDENTIFIER, ForeignKey('users.id'), nullable=True)
    department_id = Column(UNIQUEIDENTIFIER, ForeignKey('departments.id'), nullable=True)
    clinic_id = Column(UNIQUEIDENTIFIER, ForeignKey('clinics.id'), nullable=True, index=True)
    
    # Relationships
    clinic = relationship("Clinic", back_populates="doctors")
    department = relationship("Department", back_populates="doctors")
    appointments = relationship("Appointment", back_populates="doctor")
