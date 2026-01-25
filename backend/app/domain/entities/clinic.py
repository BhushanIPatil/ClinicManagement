"""
Clinic Domain Entity

Pure domain entity representing a clinic (onboarded tenant) in the system.
Each clinic has its own doctors, nurses, and employees.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Clinic:
    """
    Clinic Domain Entity

    Represents an onboarded clinic/tenant. Clinic A and Clinic B each have
    their own doctors, nurses, and employees.

    Attributes:
        id: Unique identifier
        name: Clinic name
        code: Unique clinic code
        address: Physical address
        phone: Contact phone
        is_active: Whether the clinic is active
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: UUID
    name: str
    code: str
    address: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
