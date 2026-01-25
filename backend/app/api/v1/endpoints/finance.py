"""
Finance & Billing API Endpoints

This module provides endpoints for financial management.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.core.database import db_manager
from app.infrastructure.database.models import Invoice, Payment, Patient

router = APIRouter(prefix="/finance", tags=["Finance"])


class CreateInvoiceRequest(BaseModel):
    patient_id: UUID
    appointment_id: Optional[UUID] = None
    invoice_date: datetime
    due_date: Optional[datetime] = None
    total_amount: Decimal = Field(..., ge=0)
    status: str = Field("DRAFT", description="DRAFT, PENDING, PAID, PARTIALLY_PAID, CANCELLED, OVERDUE")
    notes: Optional[str] = None


class CreatePaymentRequest(BaseModel):
    invoice_id: UUID
    amount: Decimal = Field(..., gt=0)
    payment_date: datetime
    payment_method: str = Field("CASH", description="CASH, CARD, INSURANCE, BANK_TRANSFER, etc.")
    status: str = Field("COMPLETED", description="PENDING, COMPLETED, FAILED, REFUNDED")
    reference_number: Optional[str] = None
    notes: Optional[str] = None


def _invoice_item(inv: Invoice) -> dict:
    return {
        "id": str(inv.id),
        "invoice_number": inv.invoice_number or "",
        "patient_id": str(inv.patient_id) if inv.patient_id else "",
        "appointment_id": str(inv.appointment_id) if inv.appointment_id else None,
        "invoice_date": inv.invoice_date.isoformat() if inv.invoice_date else None,
        "due_date": inv.due_date.isoformat() if inv.due_date else None,
        "status": inv.status or "DRAFT",
        "subtotal": float(inv.subtotal or 0),
        "tax_amount": float(inv.tax_amount or 0),
        "discount_amount": float(inv.discount_amount or 0),
        "total_amount": float(inv.total_amount or 0),
        "paid_amount": float(inv.paid_amount or 0),
        "balance_due": float(inv.balance_due or 0),
        "notes": inv.notes,
        "created_at": inv.created_at.isoformat() if getattr(inv, "created_at", None) else None,
    }


def _payment_item(pm: Payment) -> dict:
    return {
        "id": str(pm.id),
        "payment_number": pm.payment_number or "",
        "invoice_id": str(pm.invoice_id) if pm.invoice_id else "",
        "payment_date": pm.payment_date.isoformat() if pm.payment_date else None,
        "amount": float(pm.amount or 0),
        "payment_method": pm.payment_method or "",
        "status": pm.status or "COMPLETED",
        "reference_number": pm.reference_number,
        "notes": pm.notes,
        "created_at": pm.created_at.isoformat() if getattr(pm, "created_at", None) else None,
    }


@router.get("/invoices")
async def list_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
) -> Any:
    """List invoices with filtering."""
    db = db_manager.get_session()
    try:
        q = db.query(Invoice).filter(Invoice.is_deleted == False)
        if status:
            q = q.filter(Invoice.status == status)
        total = q.count()
        rows = q.order_by(Invoice.invoice_date.desc()).offset(skip).limit(limit).all()
        return {"items": [_invoice_item(r) for r in rows], "total": total, "skip": skip, "limit": limit}
    finally:
        db.close()


@router.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str) -> Any:
    """Get invoice by ID."""
    try:
        iid = UUID(invoice_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid invoice ID")
    db = db_manager.get_session()
    try:
        inv = db.query(Invoice).filter(Invoice.id == iid, Invoice.is_deleted == False).first()
        if not inv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
        return _invoice_item(inv)
    finally:
        db.close()


@router.post("/invoices", status_code=status.HTTP_201_CREATED)
async def create_invoice(body: CreateInvoiceRequest) -> Any:
    """Create a new invoice."""
    db = db_manager.get_session()
    try:
        patient = db.query(Patient).filter(Patient.id == body.patient_id, Patient.is_deleted == False).first()
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
        inv_num = f"INV-{uuid.uuid4().hex[:8].upper()}"
        total = body.total_amount
        inv = Invoice(
            invoice_number=inv_num,
            patient_id=body.patient_id,
            appointment_id=body.appointment_id,
            invoice_date=body.invoice_date,
            due_date=body.due_date or body.invoice_date,
            status=body.status or "DRAFT",
            subtotal=total,
            tax_amount=Decimal("0"),
            discount_amount=Decimal("0"),
            total_amount=total,
            paid_amount=Decimal("0"),
            balance_due=total,
            notes=body.notes,
        )
        db.add(inv)
        db.commit()
        db.refresh(inv)
        return _invoice_item(inv)
    finally:
        db.close()


@router.get("/payments")
async def list_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    invoice_id: Optional[str] = None,
) -> Any:
    """List payments with pagination."""
    db = db_manager.get_session()
    try:
        q = db.query(Payment).filter(Payment.is_deleted == False)
        if status:
            q = q.filter(Payment.status == status)
        if invoice_id:
            try:
                q = q.filter(Payment.invoice_id == UUID(invoice_id))
            except ValueError:
                pass
        total = q.count()
        rows = q.order_by(Payment.payment_date.desc()).offset(skip).limit(limit).all()
        return {"items": [_payment_item(r) for r in rows], "total": total, "skip": skip, "limit": limit}
    finally:
        db.close()


@router.get("/payments/{payment_id}")
async def get_payment(payment_id: str) -> Any:
    """Get payment by ID."""
    try:
        pid = UUID(payment_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payment ID")
    db = db_manager.get_session()
    try:
        pm = db.query(Payment).filter(Payment.id == pid, Payment.is_deleted == False).first()
        if not pm:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        return _payment_item(pm)
    finally:
        db.close()


@router.post("/payments", status_code=status.HTTP_201_CREATED)
async def create_payment(body: CreatePaymentRequest) -> Any:
    """Record a new payment."""
    db = db_manager.get_session()
    try:
        inv = db.query(Invoice).filter(Invoice.id == body.invoice_id, Invoice.is_deleted == False).first()
        if not inv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
        pm_num = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        pm = Payment(
            payment_number=pm_num,
            invoice_id=body.invoice_id,
            payment_date=body.payment_date,
            amount=body.amount,
            payment_method=body.payment_method or "CASH",
            status=body.status or "COMPLETED",
            reference_number=body.reference_number,
            notes=body.notes,
        )
        db.add(pm)
        inv.paid_amount = (inv.paid_amount or Decimal("0")) + body.amount
        inv.balance_due = (inv.total_amount or Decimal("0")) - inv.paid_amount
        inv.status = "PAID" if inv.balance_due <= 0 else "PARTIALLY_PAID"
        db.commit()
        db.refresh(pm)
        return _payment_item(pm)
    finally:
        db.close()


@router.get("/reports/revenue")
async def get_revenue_report(
    period: str = Query("month", pattern="^(day|week|month|year)$"),
) -> Any:
    """Get revenue report."""
    return {
        "period": period,
        "total_revenue": 0,
        "total_expenses": 0,
        "net_income": 0
    }


@router.get("/stats/summary")
async def get_finance_summary() -> Any:
    """Get financial summary statistics."""
    return {
        "total_revenue": 0,
        "pending_payments": 0,
        "overdue_invoices": 0,
        "this_month_revenue": 0
    }
