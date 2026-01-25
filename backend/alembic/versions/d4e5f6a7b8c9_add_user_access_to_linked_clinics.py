"""Add user_access column to linked_clinics (USER/EMPLOYEE)

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-01-25

Stores whether the link is for a USER or EMPLOYEE; role is already in role_id.
No separate employees or user_roles needed for clinic-linked users.
"""
from alembic import op
import sqlalchemy as sa


revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "linked_clinics",
        sa.Column("user_access", sa.String(20), nullable=False, server_default=sa.text("'USER'")),
    )


def downgrade() -> None:
    op.drop_column("linked_clinics", "user_access")
