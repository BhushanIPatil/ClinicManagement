"""Payment Model"""

from sqlalchemy import Column, String, DateTime, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.infrastructure.database.base import BaseModel


class Payment(BaseModel):
    """Payment model."""
    
    __tablename__ = "payments"
    
    payment_number = Column(String(20), unique=True, nullable=False, index=True)
    payment_date = Column(DateTime(timezone=True), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)  # CASH, CARD, INSURANCE, BANK_TRANSFER, etc.
    status = Column(String(20), default="COMPLETED", nullable=False)  # PENDING, COMPLETED, FAILED, REFUNDED
    reference_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Foreign Keys
    invoice_id = Column(UNIQUEIDENTIFIER, ForeignKey('invoices.id'), nullable=False)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="payments")
