"""Add clinic_user_feature_access (per-user permissions), drop clinic_settings

Revision ID: g7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-01-25

Replaces role-based clinic_settings with per-user feature access:
clinic_id, user_id, feature_key, allowed. Clinic admin assigns permissions per employee.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql


revision = "g7b8c9d0e1f2"
down_revision = "f6a7b8c9d0e1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop old role-based table
    op.drop_index(op.f("ix_clinic_settings_is_deleted"), table_name="clinic_settings")
    op.drop_index(op.f("ix_clinic_settings_deleted_at"), table_name="clinic_settings")
    op.drop_index(op.f("ix_clinic_settings_created_at"), table_name="clinic_settings")
    op.drop_index(op.f("ix_clinic_settings_id"), table_name="clinic_settings")
    op.drop_index(op.f("ix_clinic_settings_feature_key"), table_name="clinic_settings")
    op.drop_index(op.f("ix_clinic_settings_role_name"), table_name="clinic_settings")
    op.drop_index(op.f("ix_clinic_settings_clinic_id"), table_name="clinic_settings")
    op.drop_table("clinic_settings")

    # Create per-user feature access table
    op.create_table(
        "clinic_user_feature_access",
        sa.Column("clinic_id", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.Column("user_id", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.Column("feature_key", sa.String(50), nullable=False),
        sa.Column("allowed", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("id", mssql.UNIQUEIDENTIFIER(), nullable=False, comment="Primary key UUID"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
            comment="Timestamp when record was created",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
            comment="Timestamp when record was last updated",
        ),
        sa.Column(
            "deleted_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Timestamp when record was soft deleted",
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
            comment="Boolean flag for soft delete status",
        ),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "clinic_id", "user_id", "feature_key",
            name="uq_clinic_user_feature_access_clinic_user_feature",
        ),
    )
    op.create_index(
        op.f("ix_clinic_user_feature_access_clinic_id"),
        "clinic_user_feature_access",
        ["clinic_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_clinic_user_feature_access_user_id"),
        "clinic_user_feature_access",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_clinic_user_feature_access_feature_key"),
        "clinic_user_feature_access",
        ["feature_key"],
        unique=False,
    )
    op.create_index(
        op.f("ix_clinic_user_feature_access_id"),
        "clinic_user_feature_access",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_clinic_user_feature_access_created_at"),
        "clinic_user_feature_access",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_clinic_user_feature_access_deleted_at"),
        "clinic_user_feature_access",
        ["deleted_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_clinic_user_feature_access_is_deleted"),
        "clinic_user_feature_access",
        ["is_deleted"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_clinic_user_feature_access_is_deleted"), table_name="clinic_user_feature_access")
    op.drop_index(op.f("ix_clinic_user_feature_access_deleted_at"), table_name="clinic_user_feature_access")
    op.drop_index(op.f("ix_clinic_user_feature_access_created_at"), table_name="clinic_user_feature_access")
    op.drop_index(op.f("ix_clinic_user_feature_access_id"), table_name="clinic_user_feature_access")
    op.drop_index(op.f("ix_clinic_user_feature_access_feature_key"), table_name="clinic_user_feature_access")
    op.drop_index(op.f("ix_clinic_user_feature_access_user_id"), table_name="clinic_user_feature_access")
    op.drop_index(op.f("ix_clinic_user_feature_access_clinic_id"), table_name="clinic_user_feature_access")
    op.drop_table("clinic_user_feature_access")

    # Recreate clinic_settings (role-based) - minimal structure
    op.create_table(
        "clinic_settings",
        sa.Column("clinic_id", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.Column("role_name", sa.String(50), nullable=False),
        sa.Column("feature_key", sa.String(50), nullable=False),
        sa.Column("allowed", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("id", mssql.UNIQUEIDENTIFIER(), nullable=False, comment="Primary key UUID"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("clinic_id", "role_name", "feature_key", name="uq_clinic_settings_clinic_role_feature"),
    )
    op.create_index(op.f("ix_clinic_settings_clinic_id"), "clinic_settings", ["clinic_id"], unique=False)
    op.create_index(op.f("ix_clinic_settings_role_name"), "clinic_settings", ["role_name"], unique=False)
    op.create_index(op.f("ix_clinic_settings_feature_key"), "clinic_settings", ["feature_key"], unique=False)
    op.create_index(op.f("ix_clinic_settings_id"), "clinic_settings", ["id"], unique=False)
    op.create_index(op.f("ix_clinic_settings_created_at"), "clinic_settings", ["created_at"], unique=False)
    op.create_index(op.f("ix_clinic_settings_deleted_at"), "clinic_settings", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_clinic_settings_is_deleted"), "clinic_settings", ["is_deleted"], unique=False)
