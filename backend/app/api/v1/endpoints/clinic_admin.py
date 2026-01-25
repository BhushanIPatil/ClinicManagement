"""
Clinic Admin API

Allows Clinic Admin to add users (employees) to their clinic with roles:
NURSE, HR_OPERATIONS, RECEPTIONIST. Clinic is taken from the logged-in CLINIC_ADMIN user.
"""

import asyncio
from typing import Any, Literal, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import joinedload

from app.core.database import db_manager
from app.core.security.jwt import verify_token
from app.application.services.clinic_service import ClinicService
from app.application.services.user_service import UserService
from app.application.dto.user_dto import UserCreateRequest
from app.infrastructure.database.models import User, UserClinicRole

router = APIRouter(prefix="/clinic-admin", tags=["Clinic Admin"])


def _primary_clinic_from_user(user: Any) -> tuple[Optional[str], Optional[str]]:
    """Return (primary_clinic_id, primary_clinic_name). Prefer CLINIC_ADMIN assignment."""
    assignments = getattr(user, "clinic_role_assignments") or []
    for a in assignments:
        if getattr(getattr(a, "role", None), "name", None) == "CLINIC_ADMIN":
            clinic = getattr(a, "clinic", None)
            if clinic is not None:
                return (str(clinic.id), getattr(clinic, "name", None) or None)
    for a in assignments:
        clinic = getattr(a, "clinic", None)
        if clinic is not None:
            return (str(clinic.id), getattr(clinic, "name", None) or None)
    return (None, None)


class ClinicAdminContext:
    """Resolved from JWT: current user is CLINIC_ADMIN and their primary clinic_id."""

    def __init__(self, user_id: UUID, clinic_id: UUID):
        self.user_id = user_id
        self.clinic_id = clinic_id


def get_clinic_admin_context(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> ClinicAdminContext:
    """Validate JWT and ensure user has CLINIC_ADMIN with a clinic. Returns ClinicAdminContext."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization[7:].strip()
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user_id = UUID(payload["sub"])
    except (KeyError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db = db_manager.get_session()
    try:
        user = (
            db.query(User)
            .options(
                joinedload(User.clinic_role_assignments).options(
                    joinedload(UserClinicRole.role),
                    joinedload(UserClinicRole.clinic),
                ),
            )
            .filter(User.id == user_id, User.is_deleted == False)
            .first()
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        roles = []
        for a in getattr(user, "clinic_role_assignments") or []:
            if getattr(a, "role", None) and getattr(a.role, "name", None):
                roles.append(a.role.name)
        if "CLINIC_ADMIN" not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CLINIC_ADMIN role required",
            )
        pid, _ = _primary_clinic_from_user(user)
        if not pid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No clinic assigned to your account",
            )
        return ClinicAdminContext(user_id=user_id, clinic_id=UUID(pid))
    finally:
        db.close()

EMPLOYEE_ROLES = ("NURSE", "HR_OPERATIONS", "RECEPTIONIST", "DOCTOR")


class AddClinicEmployeeRequest(BaseModel):
    """Clinic admin adds a user or employee. User = users + linked_clinics only; Employee = users + linked_clinics + employees."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: str | None = Field(None, max_length=20)
    role: Literal["NURSE", "HR_OPERATIONS", "RECEPTIONIST", "DOCTOR"] = Field(
        ..., description="Clinic role (access)"
    )
    add_as: Literal["user", "employee"] = Field(
        "employee",
        description="user = only users table + linked_clinics; employee = users + linked_clinics + employees table",
    )


@router.post("/employees", status_code=status.HTTP_201_CREATED)
async def add_clinic_employee_current_user(
    body: AddClinicEmployeeRequest,
    ctx: ClinicAdminContext = Depends(get_clinic_admin_context),
) -> dict:
    """
    Clinic Admin: Add an employee to your clinic (clinic is taken from your login).
    No clinic_id in the request. Requires Authorization: Bearer <token> and CLINIC_ADMIN role.
    """
    return await _do_add_employee(ctx.clinic_id, body)


def _do_add_employee_sync(cid: UUID, body: AddClinicEmployeeRequest) -> dict:
    """Create user and add to linked_clinics with role + user_access (USER/EMPLOYEE). No employees or user_roles tables."""
    db = db_manager.get_session()
    try:
        clinic_svc = ClinicService(db)
        user_svc = UserService(db)
        if not clinic_svc.get_clinic_by_id(cid):
            raise ValueError("Clinic not found")
        role_name = body.role.upper()
        if role_name not in EMPLOYEE_ROLES:
            raise ValueError(f"Role must be one of: {', '.join(EMPLOYEE_ROLES)}")

        user_req = UserCreateRequest(
            email=body.email,
            username=body.username,
            password=body.password,
            first_name=body.first_name,
            last_name=body.last_name,
            phone=body.phone,
        )
        user = user_svc.create_user(user_req)
        user_access = "EMPLOYEE" if body.add_as == "employee" else "USER"
        clinic_svc.assign_user_to_clinic(user.id, cid, role_name, user_access=user_access)

        return {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "clinic_role": role_name,
                "user_access": user_access,
            },
            "employee": None,
        }
    except ValueError:
        db.rollback()
        raise
    finally:
        db.close()


async def _do_add_employee(cid: UUID, body: AddClinicEmployeeRequest) -> dict:
    """Run add-employee logic in a thread."""
    try:
        return await asyncio.to_thread(_do_add_employee_sync, cid, body)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/clinics/{clinic_id}/employees", status_code=status.HTTP_201_CREATED)
async def add_clinic_employee(clinic_id: str, body: AddClinicEmployeeRequest) -> dict:
    """
    Clinic Admin: Add an employee (user) to the clinic with role NURSE, HR_OPERATIONS, or RECEPTIONIST.
    Legacy path: clinic_id in URL. Prefer POST /clinic-admin/employees with JWT (clinic from login).
    """
    try:
        cid = UUID(clinic_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid clinic ID")
    return await _do_add_employee(cid, body)


def _list_employees_sync(cid: UUID, skip: int = 0, limit: int = 50) -> dict | None:
    """List users linked to the clinic from linked_clinics. record_type from user_access (USER/EMPLOYEE)."""
    db = db_manager.get_session()
    try:
        clinic_svc = ClinicService(db)
        if not clinic_svc.get_clinic_by_id(cid):
            return None
        users = clinic_svc.list_users_for_clinic(cid)
        total = len(users)
        out = []
        for u in users[skip : skip + limit]:
            acc = (u.get("user_access") or "USER").upper()
            record_type = "employee" if acc == "EMPLOYEE" else "user"
            out.append({
                "id": u["id"],
                "email": u.get("email") or "",
                "username": u.get("username") or "",
                "first_name": u.get("first_name"),
                "last_name": u.get("last_name"),
                "is_active": u.get("is_active", True),
                "clinic_role": u.get("clinic_role") or "—",
                "record_type": record_type,
                "employee_id": None,
                "employee_number": None,
                "is_active_empl": True,
            })
        return {"items": out, "total": total, "skip": skip, "limit": limit}
    finally:
        db.close()


@router.get("/employees")
async def list_clinic_employees_current_user(
    skip: int = 0,
    limit: int = 50,
    ctx: ClinicAdminContext = Depends(get_clinic_admin_context),
) -> dict:
    """List employees for the current user's clinic. Requires JWT and CLINIC_ADMIN."""
    result = await asyncio.to_thread(_list_employees_sync, ctx.clinic_id, skip, limit)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found")
    return result


@router.get("/clinics/{clinic_id}/employees")
async def list_clinic_employees(clinic_id: str, skip: int = 0, limit: int = 50) -> dict:
    """List employees (users) for a clinic. Legacy path with clinic_id in URL."""

    try:
        cid = UUID(clinic_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid clinic ID")

    result = await asyncio.to_thread(_list_employees_sync, cid, skip, limit)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found")
    return result
