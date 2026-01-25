"""Clinic Model"""

from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.orm import relationship
from app.infrastructure.database.base import BaseModel


class Clinic(BaseModel):
    """Clinic model. Each onboarded clinic has its own doctors, nurses, employees."""

    __tablename__ = "clinics"

    name = Column(String(200), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    address = Column(Text, nullable=True)
    phone = Column(String(30), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships (no employees table; user type/role via linked_clinics)
    user_role_assignments = relationship("UserClinicRole", back_populates="clinic")
    doctors = relationship("Doctor", back_populates="clinic")
    departments = relationship("Department", back_populates="clinic")
    payrolls = relationship("Payroll", back_populates="clinic")
