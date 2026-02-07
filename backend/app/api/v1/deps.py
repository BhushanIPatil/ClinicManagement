"""Shared API dependencies: current user from JWT, primary clinic."""

from typing import Optional
from uuid import UUID

from fastapi import Header, HTTPException, status

from app.core.database import db_manager
from app.core.security.jwt import verify_token
from app.infrastructure.database.models import User
from app.infrastructure.database.models.user_clinic_role import UserClinicRole
from sqlalchemy.orm import joinedload


def _primary_clinic_from_user(user: User) -> tuple[Optional[str], Optional[str]]:
    """Return (primary_clinic_id, primary_clinic_name). Prefer CLINIC_ADMIN."""
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


class CurrentUserContext:
    """Current user id and primary clinic from JWT."""

    def __init__(self, user_id: UUID, primary_clinic_id: Optional[str], primary_clinic_name: Optional[str]):
        self.user_id = user_id
        self.primary_clinic_id = primary_clinic_id
        self.primary_clinic_name = primary_clinic_name


def get_current_user_context(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> CurrentUserContext:
    """Validate JWT and return user id + primary clinic. Used by work-queue and my-tasks."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.replace("Bearer ", "", 1).strip()
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
        pid, pname = _primary_clinic_from_user(user)
        return CurrentUserContext(user_id=user_id, primary_clinic_id=pid, primary_clinic_name=pname)
    finally:
        db.close()
