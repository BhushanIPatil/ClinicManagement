"""User Task Model - personal tasks per user, not visible to others."""

from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.infrastructure.database.base import BaseModel


class UserTask(BaseModel):
    """Personal task for a single user (scoped by user_id)."""

    __tablename__ = "user_tasks"

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="PENDING", nullable=False)  # PENDING, IN_PROGRESS, COMPLETED, CANCELLED
    priority = Column(String(20), default="NORMAL", nullable=True)  # LOW, NORMAL, HIGH
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user_id = Column(UNIQUEIDENTIFIER, ForeignKey("users.id"), nullable=False, index=True)
