"""
Appointments API Endpoints

This module provides endpoints for appointment management.
"""

import uuid
from datetime import date, datetime, timedelta, time
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Body, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import joinedload

from app.core.database import db_manager
from app.infrastructure.database.models import Appointment, Patient, Doctor, Department

router = APIRouter(prefix="/appointments", tags=["Appointments"])


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

        items = [_item_from(a) for a in rows]
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
