"""Invoice Models"""

from sqlalchemy import Column, String, DateTime, Numeric, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.infrastructure.database.base import BaseModel


class Invoice(BaseModel):
    """Invoice model."""
    
    __tablename__ = "invoices"
    
    invoice_number = Column(String(20), unique=True, nullable=False, index=True)
    invoice_date = Column(DateTime(timezone=True), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="DRAFT", nullable=False)  # DRAFT, PENDING, PAID, PARTIALLY_PAID, CANCELLED, OVERDUE
    subtotal = Column(Numeric(12, 2), default=0, nullable=False)
    tax_amount = Column(Numeric(12, 2), default=0, nullable=False)
    discount_amount = Column(Numeric(12, 2), default=0, nullable=False)
    total_amount = Column(Numeric(12, 2), default=0, nullable=False)
    paid_amount = Column(Numeric(12, 2), default=0, nullable=False)
    balance_due = Column(Numeric(12, 2), default=0, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Foreign Keys
    patient_id = Column(UNIQUEIDENTIFIER, ForeignKey('patients.id'), nullable=False)
    appointment_id = Column(UNIQUEIDENTIFIER, ForeignKey('appointments.id'), nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice")


class InvoiceItem(BaseModel):
    """Invoice line item model."""
    
    __tablename__ = "invoice_items"
    
    description = Column(String(255), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    discount = Column(Numeric(12, 2), default=0, nullable=False)
    tax_rate = Column(Numeric(5, 2), default=0, nullable=False)
    total = Column(Numeric(12, 2), nullable=False)
    
    # Foreign Keys
    invoice_id = Column(UNIQUEIDENTIFIER, ForeignKey('invoices.id'), nullable=False)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="items")
