"""
Doctors API Endpoints

GET /doctors?clinic_id=... – list doctors by clinic id (e.g. from user's primary_clinic_id in cookies).
Returns Doctor rows for that clinic. If a user has DOCTOR role for the clinic (via linked_clinics) but
no Doctor row exists, one is created so they appear in the dropdown.
"""

import uuid
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.core.database import db_manager
from app.infrastructure.database.models import Doctor, Role, User, UserClinicRole

router = APIRouter(prefix="/doctors", tags=["Doctors"])


def _str(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip() or ""


def _doctor_item(d: Doctor) -> dict:
    return {
        "id": str(d.id),
        "first_name": _str(d.first_name),
        "last_name": _str(d.last_name),
        "label": f"{_str(d.first_name)} {_str(d.last_name)}".strip() or str(d.id),
    }


@router.get("")
async def get_doctors_by_clinic(
    clinic_id: str = Query(..., description="Clinic ID (e.g. primary_clinic_id from user login)"),
    limit: int = Query(200, ge=1, le=500),
) -> Any:
    """Get all doctors for the given clinic. Uses primary_clinic_id from the logged-in user (stored in cookies).
    Ensures users with DOCTOR role for this clinic in linked_clinics have a Doctor record; creates one if missing."""
    try:
        cid = UUID(clinic_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid clinic_id",
        )
    db = db_manager.get_session()
    try:
        doctor_role = (
            db.query(Role).filter(Role.name == "DOCTOR", Role.is_deleted == False).first()
        )
        if doctor_role:
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
                    .filter(
                        Doctor.user_id == uid,
                        Doctor.clinic_id == cid,
                        Doctor.is_deleted == False,
                    )
                    .first()
                )
                if not existing:
                    user = db.query(User).filter(User.id == uid, User.is_deleted == False).first()
                    if user:
                        fn = _str(getattr(user, "first_name", None)) or "Doctor"
                        ln = _str(getattr(user, "last_name", None)) or "User"
                        doc_num = f"DOC-{uuid.uuid4().hex[:8].upper()}"
                        new_doc = Doctor(
                            doctor_number=doc_num,
                            first_name=fn,
                            last_name=ln,
                            user_id=uid,
                            clinic_id=cid,
                        )
                        db.add(new_doc)
            try:
                db.commit()
            except Exception:
                db.rollback()
                raise

        rows = (
            db.query(Doctor)
            .filter(Doctor.is_deleted == False, Doctor.clinic_id == cid)
            .order_by(Doctor.first_name, Doctor.last_name)
            .limit(limit)
            .all()
        )
        return {"items": [_doctor_item(d) for d in rows]}
    finally:
        db.close()
