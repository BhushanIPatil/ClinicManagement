"""Financial Transaction Model"""

from sqlalchemy import Column, String, DateTime, Numeric, Text, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.infrastructure.database.base import BaseModel


class FinancialTransaction(BaseModel):
    """Financial Transaction model for tracking all financial activities."""
    
    __tablename__ = "financial_transactions"
    
    transaction_number = Column(String(20), unique=True, nullable=False, index=True)
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    transaction_type = Column(String(50), nullable=False)  # INCOME, EXPENSE, REFUND, ADJUSTMENT
    category = Column(String(50), nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(Text, nullable=True)
    reference_type = Column(String(50), nullable=True)  # INVOICE, PAYMENT, PAYROLL, etc.
    reference_id = Column(UNIQUEIDENTIFIER, nullable=True)
    
    # Foreign Keys
    created_by_id = Column(UNIQUEIDENTIFIER, ForeignKey('users.id'), nullable=True)
