"""Target Model"""

from sqlalchemy import Column, String, Date, Numeric, Text, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.infrastructure.database.base import BaseModel


class Target(BaseModel):
    """Target/KPI model for tracking goals."""
    
    __tablename__ = "targets"
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    target_type = Column(String(50), nullable=False)  # REVENUE, PATIENTS, APPOINTMENTS, etc.
    target_value = Column(Numeric(14, 2), nullable=False)
    current_value = Column(Numeric(14, 2), default=0)
    unit = Column(String(20), nullable=True)  # COUNT, CURRENCY, PERCENTAGE
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    status = Column(String(20), default="IN_PROGRESS")  # IN_PROGRESS, ACHIEVED, MISSED
    
    # Foreign Keys
    department_id = Column(UNIQUEIDENTIFIER, ForeignKey('departments.id'), nullable=True)
    assigned_to_id = Column(UNIQUEIDENTIFIER, ForeignKey('users.id'), nullable=True)
