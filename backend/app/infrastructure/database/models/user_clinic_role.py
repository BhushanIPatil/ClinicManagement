"""Linked Clinics: users linked to clinics with a role (CLINIC_ADMIN, NURSE, HR_OPERATIONS, RECEPTIONIST)."""

from sqlalchemy import Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.infrastructure.database.base import BaseModel


class UserClinicRole(BaseModel):
    """linked_clinics table: user_id, clinic_id, role_id, user_access (USER/EMPLOYEE). One role per user per clinic."""

    __tablename__ = "linked_clinics"
    __table_args__ = (UniqueConstraint("user_id", "clinic_id", name="uq_user_clinic"),)

    user_id = Column(UNIQUEIDENTIFIER, ForeignKey("users.id"), nullable=False, index=True)
    clinic_id = Column(UNIQUEIDENTIFIER, ForeignKey("clinics.id"), nullable=False, index=True)
    role_id = Column(UNIQUEIDENTIFIER, ForeignKey("roles.id"), nullable=False, index=True)
    user_access = Column(String(20), nullable=False, default="USER", server_default="USER")  # USER | EMPLOYEE

    user = relationship("User", back_populates="clinic_role_assignments")
    clinic = relationship("Clinic", back_populates="user_role_assignments")
    role = relationship("Role", back_populates="user_clinic_assignments")
