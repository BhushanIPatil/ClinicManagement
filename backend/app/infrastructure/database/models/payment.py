"""Payment Model

Stores all payments: PATIENT_PAYMENT (patient + appointment) and EMPLOYEE_PAYROLL (payslip).
No invoices; all required info in this table.
"""

from sqlalchemy import Column, String, DateTime, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.infrastructure.database.base import BaseModel


class Payment(BaseModel):
    """Payment model. payment_type: PATIENT_PAYMENT | EMPLOYEE_PAYROLL."""

    __tablename__ = "payments"

    payment_number = Column(String(20), unique=True, nullable=False, index=True)
    payment_date = Column(DateTime(timezone=True), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)  # CASH, CARD, BANK_TRANSFER, etc.
    status = Column(String(20), default="COMPLETED", nullable=False)  # PENDING, COMPLETED, FAILED, REFUNDED
    payment_type = Column(String(30), nullable=False, index=True)  # PATIENT_PAYMENT, EMPLOYEE_PAYROLL
    reference_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    patient_id = Column(UNIQUEIDENTIFIER, ForeignKey("patients.id"), nullable=True, index=True)
    appointment_id = Column(UNIQUEIDENTIFIER, ForeignKey("appointments.id"), nullable=True, index=True)
    payslip_id = Column(UNIQUEIDENTIFIER, ForeignKey("payslips.id"), nullable=True, index=True)
    clinic_id = Column(UNIQUEIDENTIFIER, ForeignKey("clinics.id"), nullable=True, index=True)

    patient = relationship("Patient", backref="payments")
    appointment = relationship("Appointment", backref="payments")
    payslip = relationship("Payslip", backref="payments")
    clinic = relationship("Clinic", backref="payments")
