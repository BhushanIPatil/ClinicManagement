"""
Role Domain Entity

Pure domain entity representing a role in the system.

Role hierarchy:
- SUPER_ADMIN: Platform owner. Sees onboarded clinics count and users.
- CLINIC_ADMIN: Per-clinic. Full access for one clinic, can add users.
- DOCTOR: Doctor in the clinic. Can view and manage appointments, patients.
- NURSE, HR_OPERATIONS, RECEPTIONIST: Employee roles within a clinic.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


# Canonical role names (must match rows in roles table)
class RoleName:
    """Standard role identifiers."""
    # Global (no clinic): platform super admin
    SUPER_ADMIN = "SUPER_ADMIN"
    # Per-clinic roles
    CLINIC_ADMIN = "CLINIC_ADMIN"
    DOCTOR = "DOCTOR"
    NURSE = "NURSE"
    HR_OPERATIONS = "HR_OPERATIONS"
    RECEPTIONIST = "RECEPTIONIST"


@dataclass
class Role:
    """
    Role Domain Entity

    Represents a role/permission group in the system.

    Attributes:
        id: Unique identifier
        name: Role name (e.g. SUPER_ADMIN, CLINIC_ADMIN)
        description: Role description
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: UUID
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Normalize role name to uppercase."""
        self.name = self.name.upper()
