"""Insurance Model"""

from sqlalchemy import Column, String, Date, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.infrastructure.database.base import BaseModel


class Insurance(BaseModel):
    """Insurance model."""
    
    __tablename__ = "insurances"
    
    policy_number = Column(String(50), unique=True, nullable=False, index=True)
    provider_name = Column(String(100), nullable=False)
    plan_name = Column(String(100), nullable=True)
    coverage_start_date = Column(Date, nullable=False)
    coverage_end_date = Column(Date, nullable=True)
    coverage_amount = Column(Numeric(12, 2), nullable=True)
    deductible = Column(Numeric(12, 2), nullable=True)
    copay_percentage = Column(Numeric(5, 2), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Foreign Keys
    patient_id = Column(UNIQUEIDENTIFIER, ForeignKey('patients.id'), nullable=False)
    
    # Relationships
    patient = relationship("Patient", back_populates="insurance")
