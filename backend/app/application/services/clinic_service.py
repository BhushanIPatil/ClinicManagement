"""
Clinic Service

Business logic for clinic (tenant) management: onboard clinics,
list clinics, assign users to clinics with roles (CLINIC_ADMIN, NURSE, HR_OPERATIONS, RECEPTIONIST).
"""

from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.infrastructure.database.models.clinic import Clinic
from app.infrastructure.database.models.user import User
from app.infrastructure.database.models.role import Role
from app.infrastructure.database.models.user_clinic_role import UserClinicRole

CLINIC_ADMIN_ROLE = "CLINIC_ADMIN"


class ClinicService:
    """Service for clinic and user-clinic-role operations."""

    def __init__(self, db: Session):
        self.db = db

    def count_clinics(self) -> int:
        """Return total number of onboarded (active, non-deleted) clinics. For Super Admin."""
        return (
            self.db.query(func.count(Clinic.id))
            .filter(Clinic.is_deleted == False, Clinic.is_active == True)
            .scalar() or 0
        )

    def list_clinics(
        self, skip: int = 0, limit: int = 50, include_inactive: bool = False
    ) -> Tuple[List[Clinic], int]:
        """
        List clinics with pagination.
        For Super Admin: all clinics; for Clinic Admin: filter by their clinic_ids elsewhere.
        """
        q = self.db.query(Clinic).filter(Clinic.is_deleted == False)
        if not include_inactive:
            q = q.filter(Clinic.is_active == True)
        total = q.count()
        items = q.order_by(Clinic.created_at.desc()).offset(skip).limit(limit).all()
        return items, total

    def get_clinic_by_id(self, clinic_id: UUID) -> Optional[Clinic]:
        """Get clinic by id."""
        return (
            self.db.query(Clinic)
            .filter(Clinic.id == clinic_id, Clinic.is_deleted == False)
            .first()
        )

    def get_clinic_by_code(self, code: str) -> Optional[Clinic]:
        """Get clinic by code."""
        return (
            self.db.query(Clinic)
            .filter(Clinic.code == code.upper().strip(), Clinic.is_deleted == False)
            .first()
        )

    def create_clinic(
        self,
        name: str,
        code: str,
        address: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> Clinic:
        """Create a new clinic. Caller should then assign a user as CLINIC_ADMIN via assign_user_to_clinic."""
        if self.get_clinic_by_code(code):
            raise ValueError(f"Clinic with code '{code}' already exists")
        clinic = Clinic(
            name=name,
            code=code.upper().strip(),
            address=address,
            phone=phone,
            is_active=True,
        )
        self.db.add(clinic)
        self.db.commit()
        self.db.refresh(clinic)
        return clinic

    def assign_user_to_clinic(
        self,
        user_id: UUID,
        clinic_id: UUID,
        role_name: str,
        user_access: str = "USER",
    ) -> UserClinicRole:
        """
        Assign a user to a clinic with a role. user_access is USER or EMPLOYEE.
        One role per user per clinic; existing assignment is replaced.
        """
        role = self.db.query(Role).filter(Role.name == role_name.upper(), Role.is_deleted == False).first()
        if not role:
            raise ValueError(f"Role '{role_name}' not found")
        user = self.db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        if not user:
            raise ValueError("User not found")
        clinic = self.get_clinic_by_id(clinic_id)
        if not clinic:
            raise ValueError("Clinic not found")
        access = (user_access or "USER").upper()
        if access not in ("USER", "EMPLOYEE"):
            access = "USER"
        existing = (
            self.db.query(UserClinicRole)
            .filter(
                UserClinicRole.user_id == user_id,
                UserClinicRole.clinic_id == clinic_id,
                UserClinicRole.is_deleted == False,
            )
            .first()
        )
        if existing:
            existing.role_id = role.id
            existing.user_access = access
            self.db.commit()
            self.db.refresh(existing)
            return existing
        ucr = UserClinicRole(user_id=user_id, clinic_id=clinic_id, role_id=role.id, user_access=access)
        self.db.add(ucr)
        self.db.commit()
        self.db.refresh(ucr)
        return ucr

    def onboard_clinic(
        self,
        name: str,
        code: str,
        admin_user_id: UUID,
        address: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> Clinic:
        """
        Onboard a new clinic and assign the given user as CLINIC_ADMIN.
        """
        clinic = self.create_clinic(name=name, code=code, address=address, phone=phone)
        self.assign_user_to_clinic(admin_user_id, clinic.id, CLINIC_ADMIN_ROLE)
        return clinic

    def onboard_clinic_with_user(
        self,
        clinic_name: str,
        clinic_code: str,
        clinic_address: Optional[str],
        clinic_phone: Optional[str],
        user_email: str,
        user_username: str,
        user_password: str,
        user_first_name: str,
        user_last_name: str,
        user_phone: Optional[str] = None,
    ) -> Tuple[Clinic, User]:
        """
        Super Admin: Create clinic + new user, store in clinic, users, linked_clinics, roles.
        The new user is linked to the clinic with role CLINIC_ADMIN (from roles table).
        """
        from app.application.services.user_service import UserService
        from app.application.dto.user_dto import UserCreateRequest

        user_svc = UserService(self.db)
        user_req = UserCreateRequest(
            email=user_email,
            username=user_username,
            password=user_password,
            first_name=user_first_name,
            last_name=user_last_name,
            phone=user_phone,
        )
        user = user_svc.create_user(user_req)
        clinic = self.create_clinic(
            name=clinic_name,
            code=clinic_code,
            address=clinic_address,
            phone=clinic_phone,
        )
        self.assign_user_to_clinic(user.id, clinic.id, CLINIC_ADMIN_ROLE)
        return clinic, user

    def list_users_for_clinic(self, clinic_id: UUID) -> List[dict]:
        """
        List users associated with a clinic (via linked_clinics).
        Returns user_access (USER/EMPLOYEE) from the link.
        """
        rows = (
            self.db.query(User, UserClinicRole, Role)
            .join(UserClinicRole, UserClinicRole.user_id == User.id)
            .join(Role, Role.id == UserClinicRole.role_id)
            .filter(
                UserClinicRole.clinic_id == clinic_id,
                UserClinicRole.is_deleted == False,
                User.is_deleted == False,
            )
            .all()
        )
        return [
            {
                "id": str(u.id),
                "email": u.email,
                "username": u.username,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "is_active": u.is_active,
                "clinic_role": r.name,
                "user_access": (ucr.user_access or "USER").upper(),
            }
            for u, ucr, r in rows
        ]
