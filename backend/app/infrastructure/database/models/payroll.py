"""Payroll Model"""

from sqlalchemy import Column, String, Date, Numeric, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.infrastructure.database.base import BaseModel


class Payroll(BaseModel):
    """Payroll model for monthly payroll processing. Scoped to a clinic (HR role handles payroll)."""
    
    __tablename__ = "payrolls"
    
    payroll_number = Column(String(20), unique=True, nullable=False, index=True)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    pay_date = Column(Date, nullable=True)
    status = Column(String(20), default="DRAFT", nullable=False)  # DRAFT, PROCESSING, COMPLETED, CANCELLED
    total_gross = Column(Numeric(14, 2), default=0)
    total_deductions = Column(Numeric(14, 2), default=0)
    total_net = Column(Numeric(14, 2), default=0)
    employee_count = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    clinic_id = Column(UNIQUEIDENTIFIER, ForeignKey("clinics.id"), nullable=True, index=True)
    
    # Relationships
    clinic = relationship("Clinic", back_populates="payrolls")
    payslips = relationship("Payslip", back_populates="payroll")
