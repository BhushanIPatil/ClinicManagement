"""
Finance API Endpoints

Summary cards and latest transactions (patient payments + employee payroll payments).
No invoices; all payment info in payments table (PATIENT_PAYMENT, EMPLOYEE_PAYROLL).
"""

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.core.database import db_manager
from app.infrastructure.database.models import Payment, Appointment, Payslip, Payroll

router = APIRouter(prefix="/finance", tags=["Finance"])


def _payment_to_transaction(pm: Payment, patient_name: Optional[str] = None, employee_label: Optional[str] = None) -> dict:
    """Build transaction item for list (patient or employee payment)."""
    out = {
        "id": str(pm.id),
        "payment_number": pm.payment_number or "",
        "payment_type": pm.payment_type or "",
        "payment_date": pm.payment_date.isoformat() if pm.payment_date else None,
        "amount": float(pm.amount or 0),
        "payment_method": pm.payment_method or "",
        "status": pm.status or "COMPLETED",
        "reference_number": pm.reference_number,
        "notes": pm.notes,
        "created_at": pm.created_at.isoformat() if getattr(pm, "created_at", None) else None,
    }
    if pm.payment_type == "PATIENT_PAYMENT":
        out["description"] = f"Patient payment" + (f" – {patient_name}" if patient_name else "")
        out["patient_id"] = str(pm.patient_id) if pm.patient_id else None
        out["appointment_id"] = str(pm.appointment_id) if pm.appointment_id else None
    else:
        out["description"] = f"Employee payroll" + (f" – {employee_label}" if employee_label else "")
        out["payslip_id"] = str(pm.payslip_id) if pm.payslip_id else None
    return out


@router.get("/summary")
async def get_finance_summary(clinic_id: Optional[str] = Query(None)) -> Any:
    """Summary cards: total patient payments, total employee payments, counts, this month."""
    db = db_manager.get_session()
    try:
        q_patient = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
            Payment.is_deleted == False,
            Payment.payment_type == "PATIENT_PAYMENT",
            Payment.status == "COMPLETED",
        )
        q_employee = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
            Payment.is_deleted == False,
            Payment.payment_type == "EMPLOYEE_PAYROLL",
            Payment.status == "COMPLETED",
        )
        if clinic_id:
            try:
                cid = UUID(clinic_id)
                q_patient = q_patient.filter(Payment.clinic_id == cid)
                q_employee = q_employee.filter(Payment.clinic_id == cid)
            except ValueError:
                pass
        total_patient = float(q_patient.scalar() or 0)
        total_employee = float(q_employee.scalar() or 0)

        cnt_patient = db.query(func.count(Payment.id)).filter(
            Payment.is_deleted == False,
            Payment.payment_type == "PATIENT_PAYMENT",
            Payment.status == "COMPLETED",
        ).scalar() or 0
        cnt_employee = db.query(func.count(Payment.id)).filter(
            Payment.is_deleted == False,
            Payment.payment_type == "EMPLOYEE_PAYROLL",
            Payment.status == "COMPLETED",
        ).scalar() or 0

        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        this_month_patient = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
            Payment.is_deleted == False,
            Payment.payment_type == "PATIENT_PAYMENT",
            Payment.status == "COMPLETED",
            Payment.payment_date >= month_start,
        ).scalar() or 0
        this_month_employee = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
            Payment.is_deleted == False,
            Payment.payment_type == "EMPLOYEE_PAYROLL",
            Payment.status == "COMPLETED",
            Payment.payment_date >= month_start,
        ).scalar() or 0

        return {
            "total_patient_payments": total_patient,
            "total_employee_payments": total_employee,
            "total_transactions": float(total_patient) + float(total_employee),
            "patient_payments_count": cnt_patient,
            "employee_payments_count": cnt_employee,
            "this_month_patient_payments": float(this_month_patient),
            "this_month_employee_payments": float(this_month_employee),
        }
    finally:
        db.close()


@router.get("/transactions")
async def list_latest_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    payment_type: Optional[str] = Query(None, description="PATIENT_PAYMENT or EMPLOYEE_PAYROLL"),
    clinic_id: Optional[str] = Query(None),
) -> Any:
    """Latest transactions (patient payments and/or employee payroll)."""
    db = db_manager.get_session()
    try:
        q = db.query(Payment).filter(Payment.is_deleted == False)
        if payment_type:
            q = q.filter(Payment.payment_type == payment_type.upper())
        if clinic_id:
            try:
                cid = UUID(clinic_id)
                q = q.filter(Payment.clinic_id == cid)
            except ValueError:
                pass
        total = q.count()
        rows = (
            q.options(
                joinedload(Payment.patient),
                joinedload(Payment.appointment),
                joinedload(Payment.payslip).joinedload(Payslip.payroll),
            )
            .order_by(Payment.payment_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        items = []
        for pm in rows:
            patient_name = None
            if pm.patient:
                patient_name = f"{getattr(pm.patient, 'first_name', '') or ''} {getattr(pm.patient, 'last_name', '') or ''}".strip() or None
            employee_label = None
            if pm.payslip and pm.payslip.payroll:
                employee_label = f"Payroll {pm.payslip.payroll.payroll_number or pm.payslip.payslip_number}"
            items.append(_payment_to_transaction(pm, patient_name=patient_name, employee_label=employee_label))
        return {"items": items, "total": total, "skip": skip, "limit": limit}
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
        pm = (
            db.query(Payment)
            .options(
                joinedload(Payment.patient),
                joinedload(Payment.appointment),
                joinedload(Payment.payslip).joinedload(Payslip.payroll),
            )
            .filter(Payment.id == pid, Payment.is_deleted == False)
            .first()
        )
        if not pm:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        patient_name = None
        if pm.patient:
            patient_name = f"{getattr(pm.patient, 'first_name', '') or ''} {getattr(pm.patient, 'last_name', '') or ''}".strip() or None
        employee_label = None
        if pm.payslip and pm.payslip.payroll:
            employee_label = f"Payroll {pm.payslip.payroll.payroll_number or pm.payslip.payslip_number}"
        return _payment_to_transaction(pm, patient_name=patient_name, employee_label=employee_label)
    finally:
        db.close()
