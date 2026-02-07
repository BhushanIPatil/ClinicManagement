"""Clinic User Feature Access Model

Stores per-clinic, per-user feature access (which employee can access Finance, Patients, Work Queue, Payroll).
Clinic admin grants/revokes access per user; each user has their own permissions.
"""

from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.infrastructure.database.base import BaseModel


class ClinicUserFeatureAccess(BaseModel):
    """Per-clinic, per-user feature access. One row per (clinic_id, user_id, feature_key)."""

    __tablename__ = "clinic_user_feature_access"

    clinic_id = Column(UNIQUEIDENTIFIER, ForeignKey("clinics.id"), nullable=False, index=True)
    user_id = Column(UNIQUEIDENTIFIER, ForeignKey("users.id"), nullable=False, index=True)
    feature_key = Column(String(50), nullable=False, index=True)  # FINANCE, PATIENTS, WORK_QUEUE, PAYROLL
    allowed = Column(Boolean, default=True, nullable=False)

    clinic = relationship("Clinic", backref="user_feature_access")
    user = relationship("User", backref="clinic_feature_access")
