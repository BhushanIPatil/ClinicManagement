"""Payroll Assignment Model – links a user to payroll for a clinic with joining date, role, salary structure, payment status."""

from sqlalchemy import Column, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.infrastructure.database.base import BaseModel


class PayrollAssignment(BaseModel):
    """User included in payroll for a clinic. One row per (user_id, clinic_id)."""

    __tablename__ = "payroll_assignments"

    user_id = Column(UNIQUEIDENTIFIER, ForeignKey("users.id"), nullable=False, index=True)
    clinic_id = Column(UNIQUEIDENTIFIER, ForeignKey("clinics.id"), nullable=False, index=True)
    joining_date = Column(Date, nullable=False)
    role = Column(String(50), nullable=False)  # e.g. NURSE, HR_OPERATIONS, DOCTOR, RECEPTIONIST
    salary_structure_id = Column(UNIQUEIDENTIFIER, ForeignKey("salary_structures.id"), nullable=True, index=True)
    payment_status = Column(String(20), default="PENDING", nullable=False)  # PENDING, PAID, PARTIAL
    last_payment_date = Column(Date, nullable=True)
    created_by_id = Column(UNIQUEIDENTIFIER, ForeignKey("users.id"), nullable=True, index=True)
    updated_by_id = Column(UNIQUEIDENTIFIER, ForeignKey("users.id"), nullable=True, index=True)

    user = relationship("User", foreign_keys=[user_id])
    clinic = relationship("Clinic", foreign_keys=[clinic_id])
    salary_structure = relationship("SalaryStructure", foreign_keys=[salary_structure_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
    updated_by = relationship("User", foreign_keys=[updated_by_id])
