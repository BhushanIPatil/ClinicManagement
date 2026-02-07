"""Salary Structure Model"""

from sqlalchemy import Column, String, Numeric, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.infrastructure.database.base import BaseModel


class SalaryStructure(BaseModel):
    """Salary Structure model."""
    
    __tablename__ = "salary_structures"
    
    base_salary = Column(Numeric(12, 2), nullable=False)
    housing_allowance = Column(Numeric(12, 2), default=0)
    transport_allowance = Column(Numeric(12, 2), default=0)
    medical_allowance = Column(Numeric(12, 2), default=0)
    other_allowances = Column(Numeric(12, 2), default=0)
    tax_deduction = Column(Numeric(12, 2), default=0)
    insurance_deduction = Column(Numeric(12, 2), default=0)
    other_deductions = Column(Numeric(12, 2), default=0)
    gross_salary = Column(Numeric(12, 2), nullable=False)
    net_salary = Column(Numeric(12, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Foreign Keys (employees table dropped; employee_id kept as plain column for legacy data)
    employee_id = Column(UNIQUEIDENTIFIER, nullable=True)
    user_id = Column(UNIQUEIDENTIFIER, ForeignKey("users.id"), nullable=True, index=True)

    user = relationship("User", foreign_keys=[user_id])
