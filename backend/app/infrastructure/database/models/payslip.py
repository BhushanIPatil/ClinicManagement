"""Payslip Model"""

from sqlalchemy import Column, String, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.infrastructure.database.base import BaseModel


class Payslip(BaseModel):
    """Payslip model."""
    
    __tablename__ = "payslips"
    
    payslip_number = Column(String(20), unique=True, nullable=False, index=True)
    base_salary = Column(Numeric(12, 2), nullable=False)
    total_allowances = Column(Numeric(12, 2), default=0)
    total_deductions = Column(Numeric(12, 2), default=0)
    gross_salary = Column(Numeric(12, 2), nullable=False)
    net_salary = Column(Numeric(12, 2), nullable=False)
    overtime_pay = Column(Numeric(12, 2), default=0)
    bonus = Column(Numeric(12, 2), default=0)
    status = Column(String(20), default="GENERATED", nullable=False)  # GENERATED, SENT, PAID
    notes = Column(Text, nullable=True)
    
    # Foreign Keys (employees table dropped; employee_id kept as plain column for legacy data)
    employee_id = Column(UNIQUEIDENTIFIER, nullable=True)
    user_id = Column(UNIQUEIDENTIFIER, ForeignKey("users.id"), nullable=True, index=True)
    payroll_id = Column(UNIQUEIDENTIFIER, ForeignKey('payrolls.id'), nullable=False)
    
    # Relationships
    payroll = relationship("Payroll", back_populates="payslips")
    user = relationship("User", foreign_keys=[user_id])
