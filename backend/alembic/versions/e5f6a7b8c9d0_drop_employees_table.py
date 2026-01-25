"""Drop employees table after removing FK constraints that reference it

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-01-25

Removes all foreign key constraints that reference employees, then drops the
employees table. Tables affected: attendances, payslips, salary_structures.
"""
from alembic import op
from sqlalchemy import inspect


revision = "e5f6a7b8c9d0"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    # Find and drop every FK that references employees (referred_table can be "employees" or "dbo.employees" etc.)
    for table in ["attendances", "payslips", "salary_structures"]:
        try:
            for fk in inspector.get_foreign_keys(table):
                ref = fk.get("referred_table") or ""
                if ref == "employees" or ref.endswith(".employees"):
                    op.drop_constraint(fk["name"], table, type_="foreignkey")
        except Exception:
            pass  # table might not exist in some envs
    op.drop_table("employees")


def downgrade() -> None:
    # Recreating employees and its FKs would require full table definition and existing constraints.
    # Not implemented; restore from backup if needed.
    pass
