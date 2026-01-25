"""
Patients API Endpoints

List, create, get, and update patients. Used before setting up appointments.
"""

import uuid
from datetime import date
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import or_

from app.core.database import db_manager
from app.infrastructure.database.models import Patient

router = APIRouter(prefix="/patients", tags=["Patients"])


class CreatePatientRequest(BaseModel):
    patient_number: Optional[str] = Field(None, max_length=20)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: Optional[str] = None  # ISO date YYYY-MM-DD
    gender: Optional[str] = Field(None, description="MALE, FEMALE, OTHER")
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None


class UpdatePatientRequest(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None


def _str(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip() or ""


def _parse_date(s: Optional[str]) -> Optional[date]:
    if not s or not _str(s):
        return None
    try:
        return date.fromisoformat(_str(s).split("T")[0])
    except (ValueError, TypeError):
        return None


def _item_from(p: Patient) -> dict:
    return {
        "id": str(p.id),
        "patient_number": _str(p.patient_number),
        "first_name": _str(p.first_name),
        "last_name": _str(p.last_name),
        "date_of_birth": p.date_of_birth.isoformat() if p.date_of_birth else None,
        "gender": _str(p.gender) or None,
        "email": _str(p.email) or None,
        "phone": _str(p.phone) or None,
        "address": _str(p.address) or None,
        "emergency_contact_name": _str(p.emergency_contact_name) or None,
        "emergency_contact_phone": _str(p.emergency_contact_phone) or None,
        "blood_type": _str(p.blood_type) or None,
        "allergies": _str(p.allergies) or None,
        "created_at": p.created_at.isoformat() if getattr(p, "created_at", None) else None,
        "updated_at": p.updated_at.isoformat() if getattr(p, "updated_at", None) else None,
    }


@router.get("")
async def list_patients(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
) -> Any:
    """List patients with optional search. Returns items + total for consistency with frontend."""
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
                    Patient.phone.like(term),
                )
            )
        total = q.count()
        rows = (
            q.order_by(Patient.first_name, Patient.last_name)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        items = [_item_from(r) for r in rows]
        return {"items": items, "patients": items, "total": total, "page": page, "page_size": page_size}
    finally:
        db.close()


@router.get("/{patient_id}")
async def get_patient(patient_id: str) -> Any:
    """Get patient by ID."""
    try:
        pid = UUID(patient_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid patient ID")
    db = db_manager.get_session()
    try:
        p = db.query(Patient).filter(Patient.id == pid, Patient.is_deleted == False).first()
        if not p:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
        return _item_from(p)
    finally:
        db.close()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_patient(body: CreatePatientRequest) -> Any:
    """Create a new patient. patient_number is optional and will be auto-generated if omitted."""
    db = db_manager.get_session()
    try:
        pn = _str(body.patient_number)
        if not pn:
            pn = f"PAT-{uuid.uuid4().hex[:8].upper()}"
        existing = db.query(Patient).filter(Patient.patient_number == pn, Patient.is_deleted == False).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Patient number already exists: {pn}",
            )
        dob = _parse_date(body.date_of_birth)
        p = Patient(
            patient_number=pn,
            first_name=_str(body.first_name) or "Unknown",
            last_name=_str(body.last_name) or "Unknown",
            date_of_birth=dob,
            gender=_str(body.gender) or None,
            email=_str(body.email) or None,
            phone=_str(body.phone) or None,
            address=_str(body.address) or None,
            emergency_contact_name=_str(body.emergency_contact_name) or None,
            emergency_contact_phone=_str(body.emergency_contact_phone) or None,
            blood_type=_str(body.blood_type) or None,
            allergies=_str(body.allergies) or None,
        )
        db.add(p)
        db.commit()
        db.refresh(p)
        return _item_from(p)
    finally:
        db.close()


@router.put("/{patient_id}")
async def update_patient(patient_id: str, body: UpdatePatientRequest) -> Any:
    """Update patient by ID."""
    try:
        pid = UUID(patient_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid patient ID")
    db = db_manager.get_session()
    try:
        p = db.query(Patient).filter(Patient.id == pid, Patient.is_deleted == False).first()
        if not p:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
        if body.first_name is not None:
            p.first_name = _str(body.first_name) or p.first_name
        if body.last_name is not None:
            p.last_name = _str(body.last_name) or p.last_name
        if body.date_of_birth is not None:
            p.date_of_birth = _parse_date(body.date_of_birth)
        if body.gender is not None:
            p.gender = _str(body.gender) or None
        if body.email is not None:
            p.email = _str(body.email) or None
        if body.phone is not None:
            p.phone = _str(body.phone) or None
        if body.address is not None:
            p.address = _str(body.address) or None
        if body.emergency_contact_name is not None:
            p.emergency_contact_name = _str(body.emergency_contact_name) or None
        if body.emergency_contact_phone is not None:
            p.emergency_contact_phone = _str(body.emergency_contact_phone) or None
        if body.blood_type is not None:
            p.blood_type = _str(body.blood_type) or None
        if body.allergies is not None:
            p.allergies = _str(body.allergies) or None
        db.commit()
        db.refresh(p)
        return _item_from(p)
    finally:
        db.close()
