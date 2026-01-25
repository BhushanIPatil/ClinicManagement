"""Attendance Model"""

from sqlalchemy import Column, String, Date, Time, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.infrastructure.database.base import BaseModel


class Attendance(BaseModel):
    """Attendance model."""
    
    __tablename__ = "attendances"
    
    attendance_date = Column(Date, nullable=False, index=True)
    check_in_time = Column(Time, nullable=True)
    check_out_time = Column(Time, nullable=True)
    status = Column(String(20), default="PRESENT", nullable=False)  # PRESENT, ABSENT, LATE, HALF_DAY, LEAVE
    hours_worked = Column(Numeric(5, 2), nullable=True)
    overtime_hours = Column(Numeric(5, 2), default=0)
    notes = Column(Text, nullable=True)
    
    # Foreign Keys (employees table dropped; employee_id kept as plain column for legacy data)
    employee_id = Column(UNIQUEIDENTIFIER, nullable=True)
