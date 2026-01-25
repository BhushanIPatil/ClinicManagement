"""Employee model - table dropped; roles/user-access via linked_clinics only.
Kept for backward compatibility in imports; do not use for DB queries.
"""

from sqlalchemy import Column, String, Date, Numeric, Boolean
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.infrastructure.database.base import BaseModel


class EmployeeRole:
    NURSE = "NURSE"
    HR_OPERATIONS = "HR_OPERATIONS"
    RECEPTIONIST = "RECEPTIONIST"


class Employee(BaseModel):
    """Legacy model; employees table has been dropped. Use linked_clinics.user_access instead."""

    __tablename__ = "employees"

    employee_number = Column(String(20), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    hire_date = Column(Date, nullable=True)
    job_title = Column(String(100), nullable=True)
    salary = Column(Numeric(12, 2), nullable=True)
    employee_role = Column(String(50), nullable=True)
    is_active = Column(Boolean, nullable=True)
    user_id = Column(UNIQUEIDENTIFIER, nullable=True)
    department_id = Column(UNIQUEIDENTIFIER, nullable=True)
    clinic_id = Column(UNIQUEIDENTIFIER, nullable=True)
