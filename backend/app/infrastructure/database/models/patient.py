"""Patient Model"""

from sqlalchemy import Column, String, Date, Text
from sqlalchemy.orm import relationship
from app.infrastructure.database.base import BaseModel


class Patient(BaseModel):
    """Patient model."""
    
    __tablename__ = "patients"
    
    patient_number = Column(String(20), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)  # MALE, FEMALE, OTHER
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    blood_type = Column(String(10), nullable=True)
    allergies = Column(Text, nullable=True)
    medical_notes = Column(Text, nullable=True)
    
    # Relationships
    appointments = relationship("Appointment", back_populates="patient")
    insurance = relationship("Insurance", back_populates="patient", uselist=False)
