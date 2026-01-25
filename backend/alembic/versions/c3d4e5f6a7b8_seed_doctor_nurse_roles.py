"""Seed DOCTOR and NURSE roles in roles table

Revision ID: c3d4e5f6a7b8
Revises: a2b3c4d5e6f7
Create Date: 2026-01-25

Adds DOCTOR and NURSE to the roles table if they do not already exist.
Other roles (SUPER_ADMIN, CLINIC_ADMIN, HR_OPERATIONS, RECEPTIONIST) are
seeded by a2b3c4d5e6f7; this migration ensures DOCTOR and NURSE are present.
"""
from alembic import op
import sqlalchemy as sa
import uuid


revision = "c3d4e5f6a7b8"
down_revision = "a2b3c4d5e6f7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    roles = [
        ("DOCTOR", "Doctor in the clinic. Can view and manage appointments, patients."),
        ("NURSE", "Nurse in the clinic. Clinical support role."),
    ]
    for name, desc in roles:
        existing = conn.execute(sa.text("SELECT id FROM roles WHERE name = :name"), {"name": name}).fetchone()
        if not existing:
            conn.execute(
                sa.text(
                    "INSERT INTO roles (id, name, description, created_at, updated_at, deleted_at, is_deleted) "
                    "VALUES (:id, :name, :desc, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL, 0)"
                ),
                {"id": str(uuid.uuid4()), "name": name, "desc": desc},
            )


def downgrade() -> None:
    # Optional: remove DOCTOR and NURSE from roles (uncomment if desired)
    # op.execute("DELETE FROM roles WHERE name IN ('DOCTOR', 'NURSE')")
    pass
