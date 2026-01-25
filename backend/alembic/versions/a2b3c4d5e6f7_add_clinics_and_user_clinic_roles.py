"""Add clinics, user_clinic_roles, clinic_id on doctors/employees/departments/payrolls, employee_role, seed roles

Revision ID: a2b3c4d5e6f7
Revises: b1dda8e2dda1
Create Date: 2026-01-25

- Super Admin: platform owner, sees clinics count and users
- Clinic Admin: per-clinic, full access, can add users
- Nurse, HR_OPERATIONS, Receptionist: employee roles in a clinic
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

# revision identifiers
revision = "a2b3c4d5e6f7"
down_revision = "b1dda8e2dda1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1) Create clinics table
    op.create_table(
        "clinics",
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column(
            "id",
            mssql.UNIQUEIDENTIFIER(),
            nullable=False,
            comment="Primary key UUID",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name=op.f("uq_clinics_code")),
    )
    op.create_index(op.f("ix_clinics_code"), "clinics", ["code"], unique=True)
    op.create_index(op.f("ix_clinics_created_at"), "clinics", ["created_at"], unique=False)
    op.create_index(op.f("ix_clinics_deleted_at"), "clinics", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_clinics_id"), "clinics", ["id"], unique=False)
    op.create_index(op.f("ix_clinics_is_deleted"), "clinics", ["is_deleted"], unique=False)
    op.create_index(op.f("ix_clinics_name"), "clinics", ["name"], unique=False)

    # 2) Create linked_clinics table (users linked to clinics with role)
    op.create_table(
        "linked_clinics",
        sa.Column("user_id", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.Column("clinic_id", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.Column("role_id", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.Column("id", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"], name=op.f("fk_linked_clinics_clinic_id_clinics")),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], name=op.f("fk_linked_clinics_role_id_roles")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_linked_clinics_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_linked_clinics")),
        sa.UniqueConstraint("user_id", "clinic_id", name="uq_linked_clinics_user_clinic"),
    )
    op.create_index(op.f("ix_linked_clinics_clinic_id"), "linked_clinics", ["clinic_id"], unique=False)
    op.create_index(op.f("ix_linked_clinics_created_at"), "linked_clinics", ["created_at"], unique=False)
    op.create_index(op.f("ix_linked_clinics_deleted_at"), "linked_clinics", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_linked_clinics_id"), "linked_clinics", ["id"], unique=False)
    op.create_index(op.f("ix_linked_clinics_is_deleted"), "linked_clinics", ["is_deleted"], unique=False)
    op.create_index(op.f("ix_linked_clinics_role_id"), "linked_clinics", ["role_id"], unique=False)
    op.create_index(op.f("ix_linked_clinics_user_id"), "linked_clinics", ["user_id"], unique=False)

    # 3) Add clinic_id to doctors
    op.add_column("doctors", sa.Column("clinic_id", mssql.UNIQUEIDENTIFIER(), nullable=True))
    op.create_foreign_key(op.f("fk_doctors_clinic_id_clinics"), "doctors", "clinics", ["clinic_id"], ["id"])
    op.create_index(op.f("ix_doctors_clinic_id"), "doctors", ["clinic_id"], unique=False)

    # 4) Add clinic_id, employee_role, is_active to employees (is_active default 1)
    op.add_column("employees", sa.Column("clinic_id", mssql.UNIQUEIDENTIFIER(), nullable=True))
    op.add_column("employees", sa.Column("employee_role", sa.String(length=50), nullable=True))
    op.add_column("employees", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")))
    op.create_foreign_key(op.f("fk_employees_clinic_id_clinics"), "employees", "clinics", ["clinic_id"], ["id"])
    op.create_index(op.f("ix_employees_clinic_id"), "employees", ["clinic_id"], unique=False)
    op.create_index(op.f("ix_employees_employee_role"), "employees", ["employee_role"], unique=False)

    # 5) Add clinic_id to departments (and drop unique on code if we need code per-clinic; keep as-is for now)
    op.add_column("departments", sa.Column("clinic_id", mssql.UNIQUEIDENTIFIER(), nullable=True))
    op.create_foreign_key(op.f("fk_departments_clinic_id_clinics"), "departments", "clinics", ["clinic_id"], ["id"])
    op.create_index(op.f("ix_departments_clinic_id"), "departments", ["clinic_id"], unique=False)

    # 6) Add clinic_id to payrolls
    op.add_column("payrolls", sa.Column("clinic_id", mssql.UNIQUEIDENTIFIER(), nullable=True))
    op.create_foreign_key(op.f("fk_payrolls_clinic_id_clinics"), "payrolls", "clinics", ["clinic_id"], ["id"])
    op.create_index(op.f("ix_payrolls_clinic_id"), "payrolls", ["clinic_id"], unique=False)

    # 7) Seed roles: SUPER_ADMIN, CLINIC_ADMIN, NURSE, HR_OPERATIONS, RECEPTIONIST
    import uuid
    conn = op.get_bind()
    roles = [
        ("SUPER_ADMIN", "Platform super admin. Sees onboarded clinics count and users."),
        ("CLINIC_ADMIN", "Clinic admin. Full access for the clinic, can add users."),
        ("NURSE", "Nurse in the clinic."),
        ("HR_OPERATIONS", "HR operations. Can handle payroll."),
        ("RECEPTIONIST", "Receptionist. Can handle appointments and work queue."),
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
    # Remove seed roles (by name) – optional, leaves data
    # op.execute("DELETE FROM roles WHERE name IN ('SUPER_ADMIN','CLINIC_ADMIN','NURSE','HR_OPERATIONS','RECEPTIONIST')")

    op.drop_index(op.f("ix_payrolls_clinic_id"), table_name="payrolls")
    op.drop_constraint(op.f("fk_payrolls_clinic_id_clinics"), "payrolls", type_="foreignkey")
    op.drop_column("payrolls", "clinic_id")

    op.drop_index(op.f("ix_departments_clinic_id"), table_name="departments")
    op.drop_constraint(op.f("fk_departments_clinic_id_clinics"), "departments", type_="foreignkey")
    op.drop_column("departments", "clinic_id")

    op.drop_index(op.f("ix_employees_employee_role"), table_name="employees")
    op.drop_index(op.f("ix_employees_clinic_id"), table_name="employees")
    op.drop_constraint(op.f("fk_employees_clinic_id_clinics"), "employees", type_="foreignkey")
    op.drop_column("employees", "is_active")
    op.drop_column("employees", "employee_role")
    op.drop_column("employees", "clinic_id")

    op.drop_index(op.f("ix_doctors_clinic_id"), table_name="doctors")
    op.drop_constraint(op.f("fk_doctors_clinic_id_clinics"), "doctors", type_="foreignkey")
    op.drop_column("doctors", "clinic_id")

    op.drop_index(op.f("ix_linked_clinics_user_id"), table_name="linked_clinics")
    op.drop_index(op.f("ix_linked_clinics_role_id"), table_name="linked_clinics")
    op.drop_index(op.f("ix_linked_clinics_is_deleted"), table_name="linked_clinics")
    op.drop_index(op.f("ix_linked_clinics_id"), table_name="linked_clinics")
    op.drop_index(op.f("ix_linked_clinics_deleted_at"), table_name="linked_clinics")
    op.drop_index(op.f("ix_linked_clinics_created_at"), table_name="linked_clinics")
    op.drop_index(op.f("ix_linked_clinics_clinic_id"), table_name="linked_clinics")
    op.drop_table("linked_clinics")

    op.drop_index(op.f("ix_clinics_name"), table_name="clinics")
    op.drop_index(op.f("ix_clinics_is_deleted"), table_name="clinics")
    op.drop_index(op.f("ix_clinics_id"), table_name="clinics")
    op.drop_index(op.f("ix_clinics_deleted_at"), table_name="clinics")
    op.drop_index(op.f("ix_clinics_created_at"), table_name="clinics")
    op.drop_index(op.f("ix_clinics_code"), table_name="clinics")
    op.drop_table("clinics")
