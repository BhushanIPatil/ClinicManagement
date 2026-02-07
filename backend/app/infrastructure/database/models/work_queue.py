"""Work Queue Model - clinic-level future work and tasks."""

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.infrastructure.database.base import BaseModel


class WorkQueue(BaseModel):
    """Work Queue model for clinic-level priority tasks (visible to clinic users)."""

    __tablename__ = "work_queues"

    queue_number = Column(String(20), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(20), default="NORMAL", nullable=False)  # LOW, NORMAL, HIGH, URGENT
    status = Column(String(20), default="PENDING", nullable=False)  # PENDING, IN_PROGRESS, COMPLETED, CANCELLED
    entity_type = Column(String(50), nullable=True)  # APPOINTMENT, PATIENT, TASK, etc.
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)

    # Foreign Keys
    clinic_id = Column(UNIQUEIDENTIFIER, ForeignKey("clinics.id"), nullable=True, index=True)  # clinic-scoped
    entity_id = Column(UNIQUEIDENTIFIER, nullable=True)
    appointment_id = Column(UNIQUEIDENTIFIER, ForeignKey("appointments.id"), nullable=True)
    assigned_to_id = Column(UNIQUEIDENTIFIER, ForeignKey("users.id"), nullable=True)
    created_by_id = Column(UNIQUEIDENTIFIER, ForeignKey("users.id"), nullable=True)

    # Relationships
    appointment = relationship("Appointment", back_populates="work_queue_items")
