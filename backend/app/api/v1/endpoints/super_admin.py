"""
Super Admin API

- See how many clinics are onboarded
- See users of a clinic
- Add clinic with user (creates clinic, users, linked_clinics; user is roléd as Clinic Admin)
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Any, Optional
from uuid import UUID
import asyncio

from app.core.database import db_manager
from app.application.services.clinic_service import ClinicService

router = APIRouter(prefix="/super-admin", tags=["Super Admin"])


class ClinicOnboardUser(BaseModel):
    email: str
    username: str
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None


class ClinicOnboardClinic(BaseModel):
    name: str
    code: str
    address: Optional[str] = None
    phone: Optional[str] = None


class ClinicOnboardRequest(BaseModel):
    clinic: ClinicOnboardClinic
    user: ClinicOnboardUser


@router.get("/clinics/count")
async def get_clinics_count() -> Any:
    """Super Admin: total number of onboarded clinics."""
    def do():
        db = db_manager.get_session()
        try:
            svc = ClinicService(db)
            return {"count": svc.count_clinics()}
        finally:
            db.close()
    return await asyncio.to_thread(do)


@router.get("/clinics")
async def list_clinics(skip: int = 0, limit: int = 50, include_inactive: bool = False) -> Any:
    """Super Admin: list onboarded clinics with pagination."""
    def do():
        db = db_manager.get_session()
        try:
            svc = ClinicService(db)
            items, total = svc.list_clinics(skip=skip, limit=limit, include_inactive=include_inactive)
            return {
                "items": [
                    {
                        "id": str(c.id),
                        "name": c.name,
                        "code": c.code,
                        "address": c.address,
                        "phone": c.phone,
                        "is_active": c.is_active,
                        "created_at": c.created_at.isoformat() if c.created_at else None,
                    }
                    for c in items
                ],
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        finally:
            db.close()
    return await asyncio.to_thread(do)


@router.get("/clinics/{clinic_id}/users")
async def list_clinic_users(clinic_id: str) -> Any:
    """Super Admin: list users linked to a clinic (from linked_clinics)."""
    try:
        uid = UUID(clinic_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid clinic ID")
    def do():
        db = db_manager.get_session()
        try:
            svc = ClinicService(db)
            if not svc.get_clinic_by_id(uid):
                return None
            return svc.list_users_for_clinic(uid)
        finally:
            db.close()
    out = await asyncio.to_thread(do)
    if out is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found")
    return {"users": out}


@router.post("/clinics/onboard", status_code=status.HTTP_201_CREATED)
async def onboard_clinic_with_user(body: ClinicOnboardRequest) -> Any:
    """
    Super Admin: Add clinic with user. Creates records in:
    - clinic
    - users
    - linked_clinics (user linked to clinic with role CLINIC_ADMIN from roles table)
    """
    def do():
        db = db_manager.get_session()
        try:
            svc = ClinicService(db)
            clinic, user = svc.onboard_clinic_with_user(
                clinic_name=body.clinic.name,
                clinic_code=body.clinic.code,
                clinic_address=body.clinic.address,
                clinic_phone=body.clinic.phone,
                user_email=body.user.email,
                user_username=body.user.username,
                user_password=body.user.password,
                user_first_name=body.user.first_name,
                user_last_name=body.user.last_name,
                user_phone=body.user.phone,
            )
            return {
                "clinic": {
                    "id": str(clinic.id),
                    "name": clinic.name,
                    "code": clinic.code,
                },
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "clinic_role": "CLINIC_ADMIN",
                },
            }
        except ValueError as e:
            db.rollback()
            raise e
        finally:
            db.close()
    try:
        return await asyncio.to_thread(do)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
