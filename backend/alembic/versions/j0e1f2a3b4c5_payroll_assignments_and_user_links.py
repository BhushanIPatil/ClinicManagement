"""Payroll assignments table and user_id on salary_structures / payslips

Revision ID: j0e1f2a3b4c5
Revises: i9d0e1f2a3b4
Create Date: Payroll roster: payroll_assignments (user+clinic), user_id on salary_structures and payslips.

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

revision = "j0e1f2a3b4c5"
down_revision = "i9d0e1f2a3b4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add user_id to salary_structures
    op.add_column(
        "salary_structures",
        sa.Column("user_id", mssql.UNIQUEIDENTIFIER(), nullable=True),
    )
    op.create_foreign_key(
        "fk_salary_structures_user_id",
        "salary_structures",
        "users",
        ["user_id"],
        ["id"],
    )
    op.create_index(op.f("ix_salary_structures_user_id"), "salary_structures", ["user_id"], unique=False)

    # Add user_id to payslips
    op.add_column(
        "payslips",
        sa.Column("user_id", mssql.UNIQUEIDENTIFIER(), nullable=True),
    )
    op.create_foreign_key(
        "fk_payslips_user_id",
        "payslips",
        "users",
        ["user_id"],
        ["id"],
    )
    op.create_index(op.f("ix_payslips_user_id"), "payslips", ["user_id"], unique=False)

    # Create payroll_assignments table
    op.create_table(
        "payroll_assignments",
        sa.Column("user_id", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.Column("clinic_id", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.Column("joining_date", sa.Date(), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("salary_structure_id", mssql.UNIQUEIDENTIFIER(), nullable=True),
        sa.Column("payment_status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("last_payment_date", sa.Date(), nullable=True),
        sa.Column("created_by_id", mssql.UNIQUEIDENTIFIER(), nullable=True),
        sa.Column("updated_by_id", mssql.UNIQUEIDENTIFIER(), nullable=True),
        sa.Column("id", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_payroll_assignments_user_id"),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"], name="fk_payroll_assignments_clinic_id"),
        sa.ForeignKeyConstraint(["salary_structure_id"], ["salary_structures.id"], name="fk_payroll_assignments_salary_structure_id"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], name="fk_payroll_assignments_created_by_id"),
        sa.ForeignKeyConstraint(["updated_by_id"], ["users.id"], name="fk_payroll_assignments_updated_by_id"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_payroll_assignments_id"), "payroll_assignments", ["id"], unique=False)
    op.create_index(op.f("ix_payroll_assignments_user_id"), "payroll_assignments", ["user_id"], unique=False)
    op.create_index(op.f("ix_payroll_assignments_clinic_id"), "payroll_assignments", ["clinic_id"], unique=False)
    op.create_index(op.f("ix_payroll_assignments_created_at"), "payroll_assignments", ["created_at"], unique=False)
    op.create_index(op.f("ix_payroll_assignments_is_deleted"), "payroll_assignments", ["is_deleted"], unique=False)
    op.create_unique_constraint(
        "uq_payroll_assignments_user_clinic",
        "payroll_assignments",
        ["user_id", "clinic_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_payroll_assignments_user_clinic", "payroll_assignments", type_="unique")
    op.drop_index(op.f("ix_payroll_assignments_is_deleted"), table_name="payroll_assignments")
    op.drop_index(op.f("ix_payroll_assignments_created_at"), table_name="payroll_assignments")
    op.drop_index(op.f("ix_payroll_assignments_clinic_id"), table_name="payroll_assignments")
    op.drop_index(op.f("ix_payroll_assignments_user_id"), table_name="payroll_assignments")
    op.drop_index(op.f("ix_payroll_assignments_id"), table_name="payroll_assignments")
    op.drop_table("payroll_assignments")

    op.drop_index(op.f("ix_payslips_user_id"), table_name="payslips")
    op.drop_constraint("fk_payslips_user_id", "payslips", type_="foreignkey")
    op.drop_column("payslips", "user_id")

    op.drop_index(op.f("ix_salary_structures_user_id"), table_name="salary_structures")
    op.drop_constraint("fk_salary_structures_user_id", "salary_structures", type_="foreignkey")
    op.drop_column("salary_structures", "user_id")
