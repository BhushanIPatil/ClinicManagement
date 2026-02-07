"""Payments standalone: payment_type, patient_id, appointment_id, payslip_id; drop invoices

Revision ID: h8c9d0e1f2a3
Revises: g7b8c9d0e1f2
Create Date: 2026-01-25

Store all payment info in payments table. Two flows: PATIENT_PAYMENT (patient_id, appointment_id)
and EMPLOYEE_PAYROLL (payslip_id). Remove dependency on invoices and invoice_items.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql


revision = "h8c9d0e1f2a3"
down_revision = "g7b8c9d0e1f2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add new columns to payments (nullable for now)
    op.add_column("payments", sa.Column("payment_type", sa.String(30), nullable=True))
    op.add_column("payments", sa.Column("patient_id", mssql.UNIQUEIDENTIFIER(), nullable=True))
    op.add_column("payments", sa.Column("appointment_id", mssql.UNIQUEIDENTIFIER(), nullable=True))
    op.add_column("payments", sa.Column("payslip_id", mssql.UNIQUEIDENTIFIER(), nullable=True))
    op.add_column("payments", sa.Column("clinic_id", mssql.UNIQUEIDENTIFIER(), nullable=True))

    # 2. Backfill: set payment_type and patient_id, appointment_id from invoice (MSSQL syntax)
    conn = op.get_bind()
    conn.execute(sa.text("""
        UPDATE p SET
            p.payment_type = 'PATIENT_PAYMENT',
            p.patient_id = i.patient_id,
            p.appointment_id = i.appointment_id
        FROM payments p
        INNER JOIN invoices i ON i.id = p.invoice_id
        WHERE p.invoice_id IS NOT NULL AND p.is_deleted = 0
    """))

    # 3. Set default for new rows and make payment_type non-null (MSSQL needs type_ for alter)
    op.alter_column(
        "payments",
        "payment_type",
        existing_type=sa.String(30),
        nullable=False,
        server_default=sa.text("'PATIENT_PAYMENT'"),
    )

    # 4. Drop FK (discover name for MSSQL) and column invoice_id
    try:
        r = conn.execute(sa.text(
            "SELECT name FROM sys.foreign_keys WHERE parent_object_id = OBJECT_ID('payments') AND referenced_object_id = OBJECT_ID('invoices')"
        ))
        row = r.fetchone()
        if row:
            fk_name = row[0]
            conn.execute(sa.text(f"ALTER TABLE payments DROP CONSTRAINT [{fk_name}]"))
    except Exception:
        pass
    op.drop_column("payments", "invoice_id")

    # 5. Add FKs for new columns
    op.create_foreign_key("fk_payments_patient_id", "payments", "patients", ["patient_id"], ["id"])
    op.create_foreign_key("fk_payments_appointment_id", "payments", "appointments", ["appointment_id"], ["id"])
    op.create_foreign_key("fk_payments_payslip_id", "payments", "payslips", ["payslip_id"], ["id"])
    op.create_foreign_key("fk_payments_clinic_id", "payments", "clinics", ["clinic_id"], ["id"])
    op.create_index(op.f("ix_payments_payment_type"), "payments", ["payment_type"], unique=False)
    op.create_index(op.f("ix_payments_patient_id"), "payments", ["patient_id"], unique=False)
    op.create_index(op.f("ix_payments_appointment_id"), "payments", ["appointment_id"], unique=False)
    op.create_index(op.f("ix_payments_payslip_id"), "payments", ["payslip_id"], unique=False)
    op.create_index(op.f("ix_payments_clinic_id"), "payments", ["clinic_id"], unique=False)

    # 6. Drop invoice_items then invoices
    op.drop_index(op.f("ix_invoice_items_is_deleted"), table_name="invoice_items")
    op.drop_index(op.f("ix_invoice_items_id"), table_name="invoice_items")
    op.drop_index(op.f("ix_invoice_items_deleted_at"), table_name="invoice_items")
    op.drop_index(op.f("ix_invoice_items_created_at"), table_name="invoice_items")
    op.drop_table("invoice_items")
    op.drop_index(op.f("ix_invoices_is_deleted"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_invoice_number"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_id"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_deleted_at"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_created_at"), table_name="invoices")
    op.drop_table("invoices")


def downgrade() -> None:
    # Recreate invoices and invoice_items (minimal), add invoice_id back to payments
    op.create_table(
        "invoices",
        sa.Column("invoice_number", sa.String(20), nullable=False),
        sa.Column("invoice_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("tax_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("paid_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("balance_due", sa.Numeric(12, 2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("patient_id", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.Column("appointment_id", mssql.UNIQUEIDENTIFIER(), nullable=True),
        sa.Column("id", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["appointment_id"], ["appointments.id"]),
    )
    op.create_index("ix_invoices_created_at", "invoices", ["created_at"])
    op.create_index("ix_invoices_deleted_at", "invoices", ["deleted_at"])
    op.create_index("ix_invoices_id", "invoices", ["id"])
    op.create_index("ix_invoices_invoice_number", "invoices", ["invoice_number"], unique=True)
    op.create_index("ix_invoices_is_deleted", "invoices", ["is_deleted"])

    op.create_table(
        "invoice_items",
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount", sa.Numeric(12, 2), nullable=False),
        sa.Column("tax_rate", sa.Numeric(5, 2), nullable=False),
        sa.Column("total", sa.Numeric(12, 2), nullable=False),
        sa.Column("invoice_id", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.Column("id", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"]),
    )
    op.create_index("ix_invoice_items_created_at", "invoice_items", ["created_at"])
    op.create_index("ix_invoice_items_deleted_at", "invoice_items", ["deleted_at"])
    op.create_index("ix_invoice_items_id", "invoice_items", ["id"])
    op.create_index("ix_invoice_items_is_deleted", "invoice_items", ["is_deleted"])

    op.drop_index(op.f("ix_payments_clinic_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_payslip_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_appointment_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_patient_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_payment_type"), table_name="payments")
    op.drop_constraint("fk_payments_clinic_id", "payments", type_="foreignkey")
    op.drop_constraint("fk_payments_payslip_id", "payments", type_="foreignkey")
    op.drop_constraint("fk_payments_appointment_id", "payments", type_="foreignkey")
    op.drop_constraint("fk_payments_patient_id", "payments", type_="foreignkey")
    op.add_column("payments", sa.Column("invoice_id", mssql.UNIQUEIDENTIFIER(), nullable=True))
    op.create_foreign_key("payments_invoice_id_fkey", "payments", "invoices", ["invoice_id"], ["id"])
    op.drop_column("payments", "clinic_id")
    op.drop_column("payments", "payslip_id")
    op.drop_column("payments", "appointment_id")
    op.drop_column("payments", "patient_id")
    op.drop_column("payments", "payment_type")
