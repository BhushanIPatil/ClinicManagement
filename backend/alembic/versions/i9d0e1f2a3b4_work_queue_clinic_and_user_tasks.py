"""Work queue clinic_id and user_tasks table

Revision ID: i9d0e1f2a3b4
Revises: h8c9d0e1f2a3
Create Date: Work queue: add clinic_id (clinic-scoped). Add user_tasks for personal tasks per user.

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

revision = "i9d0e1f2a3b4"
down_revision = "h8c9d0e1f2a3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add clinic_id to work_queues (nullable for existing rows)
    op.add_column(
        "work_queues",
        sa.Column("clinic_id", mssql.UNIQUEIDENTIFIER(), nullable=True),
    )
    op.create_foreign_key(
        "fk_work_queues_clinic_id",
        "work_queues",
        "clinics",
        ["clinic_id"],
        ["id"],
    )
    op.create_index(op.f("ix_work_queues_clinic_id"), "work_queues", ["clinic_id"], unique=False)

    # Create user_tasks table (personal tasks per user)
    op.create_table(
        "user_tasks",
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("priority", sa.String(20), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("user_id", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.Column("id", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_user_tasks_user_id"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_tasks_id"), "user_tasks", ["id"], unique=False)
    op.create_index(op.f("ix_user_tasks_user_id"), "user_tasks", ["user_id"], unique=False)
    op.create_index(op.f("ix_user_tasks_created_at"), "user_tasks", ["created_at"], unique=False)
    op.create_index(op.f("ix_user_tasks_is_deleted"), "user_tasks", ["is_deleted"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_user_tasks_is_deleted"), table_name="user_tasks")
    op.drop_index(op.f("ix_user_tasks_created_at"), table_name="user_tasks")
    op.drop_index(op.f("ix_user_tasks_user_id"), table_name="user_tasks")
    op.drop_index(op.f("ix_user_tasks_id"), table_name="user_tasks")
    op.drop_table("user_tasks")

    op.drop_index(op.f("ix_work_queues_clinic_id"), table_name="work_queues")
    op.drop_constraint("fk_work_queues_clinic_id", "work_queues", type_="foreignkey")
    op.drop_column("work_queues", "clinic_id")
