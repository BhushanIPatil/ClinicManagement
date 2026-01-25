"""Appointment Model"""

from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.infrastructure.database.base import BaseModel


class Appointment(BaseModel):
    """Appointment model."""
    
    __tablename__ = "appointments"
    
    appointment_number = Column(String(20), unique=True, nullable=False, index=True)
    appointment_date = Column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes = Column(Integer, default=30)
    status = Column(String(20), default="SCHEDULED", nullable=False)  # SCHEDULED, CONFIRMED, IN_PROGRESS, COMPLETED, CANCELLED, NO_SHOW
    appointment_type = Column(String(50), nullable=True)  # CONSULTATION, FOLLOW_UP, PROCEDURE, etc.
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    # Foreign Keys
    patient_id = Column(UNIQUEIDENTIFIER, ForeignKey('patients.id'), nullable=False)
    doctor_id = Column(UNIQUEIDENTIFIER, ForeignKey('doctors.id'), nullable=False)
    department_id = Column(UNIQUEIDENTIFIER, ForeignKey('departments.id'), nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    department = relationship("Department", back_populates="appointments")
    work_queue_items = relationship("WorkQueue", back_populates="appointment")
