"""
Appointments API Endpoints

This module provides endpoints for appointment management.
"""

import uuid
from datetime import date, datetime, timedelta, time, timezone
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Header, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import joinedload
from sqlalchemy import or_

from app.core.database import db_manager
from app.core.security.jwt import verify_token
from app.infrastructure.database.models import (
    Appointment,
    Patient,
    Doctor,
    Department,
    Invoice,
    Payment,
    Role,
    User,
    UserClinicRole,
)

router = APIRouter(prefix="/appointments", tags=["Appointments"])


async def _current_user_id(authorization: Optional[str] = Header(None, alias="Authorization")) -> UUID:
    """Dependency: extract and validate JWT, return user id."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization")
    token = authorization.replace("Bearer ", "", 1).strip()
    payload = verify_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    try:
        return UUID(payload["sub"])
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


async def _optional_current_user_id(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> Optional[UUID]:
    """Optional auth: return user id when valid Bearer token present, else None."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "", 1).strip()
    payload = verify_token(token)
    if not payload or "sub" not in payload:
        return None
    try:
        return UUID(payload["sub"])
    except (ValueError, TypeError):
        return None


class CreateAppointmentRequest(BaseModel):
    patient_id: UUID
    doctor_id: UUID
    department_id: Optional[UUID] = None
    appointment_date: datetime
    duration_minutes: int = Field(30, ge=1, le=480)
    status: str = Field("SCHEDULED", description="SCHEDULED, CONFIRMED, IN_PROGRESS, COMPLETED, CANCELLED, NO_SHOW")
    appointment_type: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None


class UpdateAppointmentRequest(BaseModel):
    appointment_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=1, le=480)
    status: Optional[str] = None
    appointment_type: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    doctor_id: Optional[UUID] = None
    department_id: Optional[UUID] = None


class CancelAppointmentRequest(BaseModel):
    reason: Optional[str] = None


class PatientPaymentRequest(BaseModel):
    """Add a patient payment for an appointment (stored in payments table / Patient Payments)."""
    amount: Decimal = Field(..., gt=0)
    payment_method: str = Field("CASH", description="CASH, CARD, INSURANCE, BANK_TRANSFER, etc.")
    payment_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def _str(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip() or ""


def _item_from(a: Appointment) -> dict:
    p, doc, dept = a.patient, a.doctor, a.department
    p_name = f"{_str(getattr(p,'first_name',''))} {_str(getattr(p,'last_name',''))}".strip() or "N/A" if p else "N/A"
    d_name = f"{_str(getattr(doc,'first_name',''))} {_str(getattr(doc,'last_name',''))}".strip() or "N/A" if doc else "N/A"
    dept_name = _str(getattr(dept, "name", None)) if dept else ""
    return {
        "id": str(a.id),
        "appointment_number": _str(a.appointment_number),
        "patient_id": str(a.patient_id) if a.patient_id else "",
        "doctor_id": str(a.doctor_id) if a.doctor_id else "",
        "department_id": str(a.department_id) if a.department_id else "",
        "appointment_date": a.appointment_date.isoformat() if a.appointment_date else "",
        "duration_minutes": int(a.duration_minutes) if a.duration_minutes is not None else 0,
        "status": _str(a.status) or "SCHEDULED",
        "appointment_type": _str(a.appointment_type) or None,
        "reason": _str(a.reason) or None,
        "notes": _str(a.notes) or None,
        "patient_name": p_name,
        "doctor_name": d_name,
        "department_name": dept_name or None,
        "created_at": a.created_at.isoformat() if getattr(a, "created_at", None) else None,
        "updated_at": a.updated_at.isoformat() if getattr(a, "updated_at", None) else None,
    }


@router.get("")
async def list_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    patient_id: Optional[str] = None,
    doctor_id: Optional[str] = None,
) -> Any:
    """List appointments with filtering and pagination. Returns items with patient_name, doctor_name; null-safe."""
    db = db_manager.get_session()
    try:
        q = (
            db.query(Appointment)
            .options(
                joinedload(Appointment.patient),
                joinedload(Appointment.doctor),
                joinedload(Appointment.department),
            )
            .filter(Appointment.is_deleted == False)
        )
        if status:
            q = q.filter(Appointment.status == status)
        if date_from:
            q = q.filter(Appointment.appointment_date >= datetime.combine(date_from, datetime.min.time()))
        if date_to:
            date_to_end = datetime.combine(date_to, time.min) + timedelta(days=1)
            q = q.filter(Appointment.appointment_date < date_to_end)
        if patient_id:
            q = q.filter(Appointment.patient_id == patient_id)
        if doctor_id:
            q = q.filter(Appointment.doctor_id == doctor_id)

        total = q.count()
        rows = q.order_by(Appointment.appointment_date.desc()).offset(skip).limit(limit).all()

        app_ids = [a.id for a in rows]
        paid_app_ids = set()
        if app_ids:
            inv_rows = (
                db.query(Invoice.appointment_id)
                .filter(
                    Invoice.is_deleted == False,
                    Invoice.appointment_id.in_(app_ids),
                    or_(
                        Invoice.status == "PAID",
                        Invoice.paid_amount >= Invoice.total_amount,
                    ),
                )
                .all()
            )
            paid_app_ids = {r[0] for r in inv_rows if r[0]}

        items = []
        for a in rows:
            out = _item_from(a)
            out["paid"] = a.id in paid_app_ids
            items.append(out)
        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    finally:
        db.close()


@router.get("/today/count")
async def get_today_appointments_count() -> Any:
    """Get count of today's appointments."""
    db = db_manager.get_session()
    try:
        from datetime import timezone
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        cnt = db.query(Appointment).filter(
            Appointment.is_deleted == False,
            Appointment.appointment_date >= today_start,
            Appointment.appointment_date < today_end,
        ).count()
        return {"count": cnt, "date": date.today().isoformat()}
    finally:
        db.close()


def _doctor_option(d: Doctor) -> dict:
    return {
        "id": str(d.id),
        "first_name": _str(d.first_name),
        "last_name": _str(d.last_name),
        "label": f"{_str(d.first_name)} {_str(d.last_name)}".strip() or str(d.id),
    }


def _ensure_doctors_for_clinic_from_linked_users(db: Any, cid: UUID) -> None:
    """Create Doctor rows for users who have DOCTOR role for this clinic (linked_clinics) but no Doctor record yet."""
    doctor_role = db.query(Role).filter(Role.name == "DOCTOR", Role.is_deleted == False).first()
    if not doctor_role:
        return
    link_rows = (
        db.query(UserClinicRole.user_id)
        .filter(
            UserClinicRole.clinic_id == cid,
            UserClinicRole.role_id == doctor_role.id,
            UserClinicRole.is_deleted == False,
        )
        .distinct()
        .all()
    )
    for (uid,) in link_rows:
        existing = (
            db.query(Doctor)
            .filter(Doctor.user_id == uid, Doctor.clinic_id == cid, Doctor.is_deleted == False)
            .first()
        )
        if not existing:
            user = db.query(User).filter(User.id == uid, User.is_deleted == False).first()
            if user:
                fn = _str(getattr(user, "first_name", None)) or "Doctor"
                ln = _str(getattr(user, "last_name", None)) or "User"
                doc_num = f"DOC-{uuid.uuid4().hex[:8].upper()}"
                db.add(
                    Doctor(
                        doctor_number=doc_num,
                        first_name=fn,
                        last_name=ln,
                        user_id=uid,
                        clinic_id=cid,
                    )
                )
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


@router.get("/options/doctors")
async def list_doctors_options(
    limit: int = Query(200, ge=1, le=500),
    clinic_id: Optional[str] = Query(None, description="Filter doctors by clinic (only doctors of this clinic)"),
    current_user_id: Optional[UUID] = Depends(_optional_current_user_id),
) -> Any:
    """List doctors for dropdowns. Returns only doctors for the given clinic. Ensures users with DOCTOR role for this clinic in linked_clinics have a Doctor record (creates if missing)."""
    db = db_manager.get_session()
    try:
        if clinic_id and _str(clinic_id):
            try:
                cid = UUID(clinic_id)
                _ensure_doctors_for_clinic_from_linked_users(db, cid)
            except ValueError:
                pass
        q = db.query(Doctor).filter(Doctor.is_deleted == False)
        if clinic_id and _str(clinic_id):
            try:
                cid = UUID(clinic_id)
                q = q.filter(Doctor.clinic_id == cid)
            except ValueError:
                pass
        rows = q.order_by(Doctor.first_name, Doctor.last_name).limit(limit).all()
        return {"items": [_doctor_option(d) for d in rows]}
    finally:
        db.close()


@router.get("/options/patients")
async def list_patients_options(
    limit: int = Query(200, ge=1, le=500),
    search: Optional[str] = Query(None),
) -> Any:
    """List patients for dropdowns (id, label). Latest added patients first. Used when adding appointments."""
    db = db_manager.get_session()
    try:
        q = db.query(Patient).filter(Patient.is_deleted == False)
        if search and _str(search):
            term = f"%{_str(search).strip()}%"
            q = q.filter(
                or_(
                    Patient.first_name.like(term),
                    Patient.last_name.like(term),
                    Patient.patient_number.like(term),
                )
            )
        rows = q.order_by(Patient.created_at.desc()).limit(limit).all()
        return {
            "items": [
                {
                    "id": str(p.id),
                    "first_name": _str(p.first_name),
                    "last_name": _str(p.last_name),
                    "patient_number": _str(getattr(p, "patient_number", "")),
                    "label": f"{_str(p.first_name)} {_str(p.last_name)}".strip() or str(p.id),
                }
                for p in rows
            ]
        }
    finally:
        db.close()


@router.get("/my-schedule")
async def get_my_schedule(
    current_user_id: UUID = Depends(_current_user_id),
    limit: int = Query(50, ge=1, le=200),
) -> Any:
    """Return the current user's appointments (when they are a doctor). Today and future only. Includes fees_paid per appointment."""
    db = db_manager.get_session()
    try:
        doc = db.query(Doctor).filter(
            Doctor.user_id == current_user_id,
            Doctor.is_deleted == False,
        ).first()
        if not doc:
            return {"items": [], "total": 0}
        from datetime import timezone
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        rows = (
            db.query(Appointment)
            .options(
                joinedload(Appointment.patient),
                joinedload(Appointment.doctor),
                joinedload(Appointment.department),
            )
            .filter(
                Appointment.is_deleted == False,
                Appointment.doctor_id == doc.id,
                Appointment.appointment_date >= today_start,
                Appointment.status != "CANCELLED",
            )
            .order_by(Appointment.appointment_date.asc())
            .limit(limit)
            .all()
        )
        app_ids = [a.id for a in rows]
        paid_app_ids = set()
        if app_ids:
            inv_rows = (
                db.query(Invoice.appointment_id)
                .filter(
                    Invoice.is_deleted == False,
                    Invoice.appointment_id.in_(app_ids),
                    or_(
                        Invoice.status == "PAID",
                        Invoice.paid_amount >= Invoice.total_amount,
                    ),
                )
                .all()
            )
            paid_app_ids = {r[0] for r in inv_rows if r[0]}
        items = []
        for a in rows:
            out = _item_from(a)
            out["fees_paid"] = a.id in paid_app_ids
            items.append(out)
        return {"items": items, "total": len(items)}
    finally:
        db.close()


@router.get("/{appointment_id}")
async def get_appointment(appointment_id: str) -> Any:
    """Get appointment by ID."""
    try:
        aid = UUID(appointment_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid appointment ID")
    db = db_manager.get_session()
    try:
        a = (
            db.query(Appointment)
            .options(
                joinedload(Appointment.patient),
                joinedload(Appointment.doctor),
                joinedload(Appointment.department),
            )
            .filter(Appointment.id == aid, Appointment.is_deleted == False)
            .first()
        )
        if not a:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
        return _item_from(a)
    finally:
        db.close()


@router.post("/{appointment_id}/payments", status_code=status.HTTP_201_CREATED)
async def add_patient_payment(appointment_id: str, body: PatientPaymentRequest) -> Any:
    """Add a patient payment for an appointment. Uses the payments table (Patient Payments). If no invoice exists for this appointment, one is created. Returns the created payment."""
    try:
        aid = UUID(appointment_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid appointment ID")
    db = db_manager.get_session()
    try:
        a = (
            db.query(Appointment)
            .options(joinedload(Appointment.patient))
            .filter(Appointment.id == aid, Appointment.is_deleted == False)
            .first()
        )
        if not a:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
        inv = (
            db.query(Invoice)
            .filter(Invoice.appointment_id == aid, Invoice.is_deleted == False)
            .first()
        )
        if not inv:
            inv_num = f"INV-{uuid.uuid4().hex[:8].upper()}"
            total = body.amount
            inv = Invoice(
                invoice_number=inv_num,
                patient_id=a.patient_id,
                appointment_id=aid,
                invoice_date=body.payment_date,
                due_date=body.payment_date,
                status="DRAFT",
                subtotal=total,
                tax_amount=Decimal("0"),
                discount_amount=Decimal("0"),
                total_amount=total,
                paid_amount=Decimal("0"),
                balance_due=total,
                notes=None,
            )
            db.add(inv)
            db.flush()
        pm_num = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        pm = Payment(
            payment_number=pm_num,
            invoice_id=inv.id,
            payment_date=body.payment_date,
            amount=body.amount,
            payment_method=body.payment_method or "CASH",
            status="COMPLETED",
            reference_number=None,
            notes=None,
        )
        db.add(pm)
        inv.paid_amount = (inv.paid_amount or Decimal("0")) + body.amount
        inv.balance_due = (inv.total_amount or Decimal("0")) - inv.paid_amount
        inv.status = "PAID" if inv.balance_due <= 0 else "PARTIALLY_PAID"
        db.commit()
        db.refresh(pm)
        return {
            "id": str(pm.id),
            "payment_number": pm_num,
            "amount": float(pm.amount or 0),
            "payment_method": body.payment_method or "CASH",
            "payment_date": pm.payment_date.isoformat() if pm.payment_date else None,
        }
    finally:
        db.close()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_appointment(body: CreateAppointmentRequest) -> Any:
    """Create a new appointment."""
    db = db_manager.get_session()
    try:
        patient = db.query(Patient).filter(Patient.id == body.patient_id, Patient.is_deleted == False).first()
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
        doctor = db.query(Doctor).filter(Doctor.id == body.doctor_id, Doctor.is_deleted == False).first()
        if not doctor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
        appt_num = f"APT-{uuid.uuid4().hex[:8].upper()}"
        a = Appointment(
            appointment_number=appt_num,
            patient_id=body.patient_id,
            doctor_id=body.doctor_id,
            department_id=body.department_id,
            appointment_date=body.appointment_date,
            duration_minutes=body.duration_minutes,
            status=body.status or "SCHEDULED",
            appointment_type=body.appointment_type,
            reason=body.reason,
            notes=body.notes,
        )
        db.add(a)
        db.commit()
        db.refresh(a)
        db.refresh(a, ["patient", "doctor", "department"])
        return _item_from(a)
    finally:
        db.close()


@router.put("/{appointment_id}")
async def update_appointment(appointment_id: str, body: UpdateAppointmentRequest) -> Any:
    """Update an existing appointment."""
    try:
        aid = UUID(appointment_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid appointment ID")
    db = db_manager.get_session()
    try:
        a = (
            db.query(Appointment)
            .options(joinedload(Appointment.patient), joinedload(Appointment.doctor), joinedload(Appointment.department))
            .filter(Appointment.id == aid, Appointment.is_deleted == False)
            .first()
        )
        if not a:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
        if body.appointment_date is not None:
            a.appointment_date = body.appointment_date
        if body.duration_minutes is not None:
            a.duration_minutes = body.duration_minutes
        if body.status is not None:
            a.status = body.status
        if body.appointment_type is not None:
            a.appointment_type = body.appointment_type
        if body.reason is not None:
            a.reason = body.reason
        if body.notes is not None:
            a.notes = body.notes
        if body.doctor_id is not None:
            a.doctor_id = body.doctor_id
        if body.department_id is not None:
            a.department_id = body.department_id
        db.commit()
        db.refresh(a)
        return _item_from(a)
    finally:
        db.close()


@router.delete("/{appointment_id}")
async def cancel_appointment(appointment_id: str, body: Optional[CancelAppointmentRequest] = Body(None)) -> Any:
    """Cancel an appointment (set status to CANCELLED)."""
    try:
        aid = UUID(appointment_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid appointment ID")
    db = db_manager.get_session()
    try:
        a = (
            db.query(Appointment)
            .options(joinedload(Appointment.patient), joinedload(Appointment.doctor), joinedload(Appointment.department))
            .filter(Appointment.id == aid, Appointment.is_deleted == False)
            .first()
        )
        if not a:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
        a.status = "CANCELLED"
        a.cancellation_reason = (body.reason if body else None) or a.cancellation_reason
        db.commit()
        db.refresh(a)
        return _item_from(a)
    finally:
        db.close()
