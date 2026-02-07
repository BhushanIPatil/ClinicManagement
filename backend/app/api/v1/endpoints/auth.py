"""
Authentication API Endpoints

This module provides authentication endpoints for user login, registration, and token management.
"""

from fastapi import APIRouter, HTTPException, status, Header
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Any, Optional
from datetime import timedelta
from uuid import UUID
import asyncio

from app.core.config import settings
from app.core.database import db_manager
from app.core.security.jwt import create_access_token, verify_token
from app.application.services.user_service import UserService
from app.application.dto.user_dto import (
    UserCreateRequest,
    UserResponse,
    LoginRequest,
)


class VerifyPasswordRequest(BaseModel):
    """Request to verify a plain-text password against a user's stored hash."""
    username: Optional[str] = Field(None, description="Username or email to identify the user")
    email: Optional[str] = Field(None, description="Email to identify the user (if username not set)")
    password: str = Field(..., description="Plain-text password to verify")


class ResetPasswordRequest(BaseModel):
    """Request to set a new password when user has forgotten the old one (cannot decrypt hash)."""
    username: Optional[str] = Field(None, description="Username to identify the user")
    email: Optional[str] = Field(None, description="Email to identify the user")
    new_password: str = Field(..., min_length=8, description="New password to set")


router = APIRouter(prefix="/auth", tags=["Authentication"])


def _primary_clinic_from_user(user: Any) -> tuple[Optional[str], Optional[str]]:
    """From user's clinic_role_assignments, return (primary_clinic_id, primary_clinic_name). Prefer CLINIC_ADMIN."""
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


def _doctor_id_for_user(user_id: Any) -> Optional[str]:
    """Return doctor_id for the given user_id if they have a linked Doctor record."""
    from app.infrastructure.database.models import Doctor
    db = db_manager.get_session()
    try:
        d = db.query(Doctor).filter(Doctor.user_id == user_id, Doctor.is_deleted == False).first()
        return str(d.id) if d else None
    finally:
        db.close()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreateRequest) -> Any:
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        
    Returns:
        UserResponse: Created user data
    """
    def do_register():
        db = db_manager.get_session()
        try:
            user_service = UserService(db)
            user = user_service.create_user(user_data)
            
            return UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                phone=user.phone,
                is_active=user.is_active,
                is_superuser=user.is_superuser,
                created_at=user.created_at,
                updated_at=user.updated_at,
                roles=[a.role.name for a in (getattr(user, "clinic_role_assignments") or []) if getattr(a, "role", None)]
            )
        except ValueError as e:
            db.rollback()
            raise e
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    try:
        return await asyncio.to_thread(do_register)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/login")
async def login(login_data: LoginRequest) -> Any:
    """
    Login with username/email and password (JSON body).
    
    Example body: {"username": "john.doe@example.com", "password": "SecurePass123"}
    
    Returns:
        dict: Access token and user info
    """
    def do_login():
        db = db_manager.get_session()
        try:
            user_service = UserService(db)
            user = user_service.authenticate_user(login_data.username, login_data.password)
            return user
        finally:
            db.close()
    
    user = await asyncio.to_thread(do_login)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires
    )
    
    clinic_roles = [a.role.name for a in (getattr(user, "clinic_role_assignments") or []) if getattr(a, "role", None)]
    all_roles = list(dict.fromkeys(clinic_roles))
    primary_clinic_id, primary_clinic_name = _primary_clinic_from_user(user)
    doctor_id = await asyncio.to_thread(_doctor_id_for_user, user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "roles": all_roles,
            "primary_clinic_id": primary_clinic_id,
            "primary_clinic_name": primary_clinic_name,
            "doctor_id": doctor_id,
        }
    }


@router.post("/login/json")
async def login_json(login_data: LoginRequest) -> Any:
    """
    JSON-based login endpoint.
    
    Args:
        login_data: Login credentials (username, password)
        
    Returns:
        dict: Access token and user info
    """
    def do_login():
        db = db_manager.get_session()
        try:
            user_service = UserService(db)
            user = user_service.authenticate_user(login_data.username, login_data.password)
            return user
        finally:
            db.close()
    
    user = await asyncio.to_thread(do_login)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires
    )
    
    clinic_roles = [a.role.name for a in (getattr(user, "clinic_role_assignments") or []) if getattr(a, "role", None)]
    all_roles = list(dict.fromkeys(clinic_roles))
    primary_clinic_id, primary_clinic_name = _primary_clinic_from_user(user)
    doctor_id = await asyncio.to_thread(_doctor_id_for_user, user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "roles": all_roles,
            "primary_clinic_id": primary_clinic_id,
            "primary_clinic_name": primary_clinic_name,
            "doctor_id": doctor_id,
        }
    }


@router.get("/me")
async def get_current_user() -> Any:
    """
    Get current user information.
    
    Note: Implement proper JWT validation.
    
    Returns:
        dict: Current user data
    """
    return {
        "message": "Implement JWT authentication to get current user",
        "hint": "Pass Authorization: Bearer <token> header"
    }


# Feature keys (must match clinic_admin.SETTINGS_FEATURES)
FEATURE_KEYS = ("FINANCE", "PATIENTS", "WORK_QUEUE", "PAYROLL")


def _get_feature_access_sync(user_id: UUID, primary_clinic_id: Optional[str], role_names: list) -> dict:
    """Return { FINANCE: bool, ... } for this user at primary clinic. CLINIC_ADMIN gets all True. Else from clinic_user_feature_access; no rows = all True (backward compat)."""
    if not primary_clinic_id:
        return {k: False for k in FEATURE_KEYS}
    if "CLINIC_ADMIN" in [r.upper() for r in role_names]:
        return {k: True for k in FEATURE_KEYS}
    try:
        cid = UUID(primary_clinic_id)
    except ValueError:
        return {k: False for k in FEATURE_KEYS}
    db = db_manager.get_session()
    try:
        from app.infrastructure.database.models import ClinicUserFeatureAccess
        rows = (
            db.query(ClinicUserFeatureAccess)
            .filter(
                ClinicUserFeatureAccess.clinic_id == cid,
                ClinicUserFeatureAccess.user_id == user_id,
                ClinicUserFeatureAccess.is_deleted == False,
            )
            .all()
        )
        if not rows:
            return {k: True for k in FEATURE_KEYS}
        allowed_features = {r.feature_key for r in rows if r.allowed}
        return {k: k in allowed_features for k in FEATURE_KEYS}
    finally:
        db.close()


@router.get("/me/feature-access")
async def get_my_feature_access(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> dict:
    """
    Return feature access for the current user (per-user permissions at primary clinic).
    CLINIC_ADMIN gets all True. Others: from clinic_user_feature_access; no rows = all True.
    Returns: { "FINANCE": bool, "PATIENTS": bool, "WORK_QUEUE": bool, "PAYROLL": bool }
    """
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
    from app.infrastructure.database.models import User, UserClinicRole
    from sqlalchemy.orm import joinedload
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
        primary_clinic_id, _ = _primary_clinic_from_user(user)
        assignments = getattr(user, "clinic_role_assignments") or []
        role_names = []
        for a in assignments:
            clinic = getattr(a, "clinic", None)
            if clinic and str(clinic.id) == primary_clinic_id:
                r = getattr(getattr(a, "role", None), "name", None)
                if r:
                    role_names.append(r)
        return await asyncio.to_thread(
            _get_feature_access_sync, user_id, primary_clinic_id, role_names
        )
    finally:
        db.close()


@router.post("/logout")
async def logout() -> Any:
    """
    Logout endpoint.
    
    Returns:
        dict: Logout confirmation
    """
    return {"message": "Successfully logged out"}


@router.post("/verify-password")
async def verify_password(body: VerifyPasswordRequest) -> Any:
    """
    Verify that a plain-text password matches a user's stored hash.

    Passwords are hashed (bcrypt), not encrypted. They cannot be decrypted or
    recovered—this endpoint only checks whether the given password is correct.

    Provide either username or email to identify the user, and the plain password.
    Returns: { "valid": true|false, "message": "..." }
    """
    identifier = body.username or body.email
    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either 'username' or 'email'",
        )

    def do_verify():
        from app.core.security.password import verify_password as verify
        db = db_manager.get_session()
        try:
            user_service = UserService(db)
            user = user_service.get_user_by_username_or_email(identifier)
            if not user:
                return {"valid": False, "message": "User not found"}
            ok = verify(body.password, user.hashed_password)
            return {"valid": ok, "message": "Password matches" if ok else "Password does not match"}
        finally:
            db.close()

    return await asyncio.to_thread(do_verify)


@router.post("/reset-password")
async def reset_password(body: ResetPasswordRequest) -> Any:
    """
    Forgot password: set a new password without knowing the old one.

    The stored password is a one-way hash—it cannot be decrypted or recovered.
    This endpoint lets the user (or an admin) set a new password instead.

    Provide either username or email to identify the account, and the new password.
    In production you would add email verification or a time-limited reset token.
    """
    identifier = body.username or body.email
    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either 'username' or 'email'",
        )

    def do_reset():
        db = db_manager.get_session()
        try:
            user_service = UserService(db)
            user_service.reset_password(identifier, body.new_password)
            return {"message": "Password has been reset. You can log in with your new password."}
        except ValueError as e:
            return {"error": str(e)}
        finally:
            db.close()

    result = await asyncio.to_thread(do_reset)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
    return result


@router.get("/users")
async def list_users(skip: int = 0, limit: int = 10) -> Any:
    """
    List all users (admin endpoint).
    
    Args:
        skip: Number of records to skip
        limit: Maximum records to return
        
    Returns:
        dict: List of users with pagination info
    """
    def do_list():
        db = db_manager.get_session()
        try:
            user_service = UserService(db)
            users, total = user_service.list_users(skip=skip, limit=limit)
            
            return {
                "items": [
                    {
                        "id": str(user.id),
                        "email": user.email,
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "is_active": user.is_active,
                        "is_superuser": user.is_superuser,
                        "created_at": user.created_at.isoformat(),
                        "roles": [a.role.name for a in (getattr(user, "clinic_role_assignments") or []) if getattr(a, "role", None)]
                    }
                    for user in users
                ],
                "total": total,
                "skip": skip,
                "limit": limit
            }
        finally:
            db.close()
    
    return await asyncio.to_thread(do_list)


@router.get("/users/{user_id}")
async def get_user(user_id: str) -> Any:
    """
    Get user by ID.
    
    Args:
        user_id: User UUID
        
    Returns:
        dict: User data
    """
    from uuid import UUID
    
    try:
        uuid_id = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    def do_get():
        db = db_manager.get_session()
        try:
            user_service = UserService(db)
            user = user_service.get_user_by_id(uuid_id)
            
            if not user:
                return None
            
            return {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
                "roles": [a.role.name for a in (getattr(user, "clinic_role_assignments") or []) if getattr(a, "role", None)]
            }
        finally:
            db.close()
    
    result = await asyncio.to_thread(do_get)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return result
