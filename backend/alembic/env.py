"""
Alembic Environment Configuration

This file configures Alembic to work with our SQLAlchemy models and database.
It automatically discovers all models that inherit from Base and includes them
in migrations.

Key Features:
- Automatic model discovery
- Environment-based database URL from settings
- Support for async migrations (future)
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import sys
from pathlib import Path

# Add the backend directory to the path so we can import our app
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Import our Base and settings
from app.infrastructure.database.base import Base
from app.core.config import settings

# Import all models here so Alembic can discover them
from app.infrastructure.database.models.user import User
from app.infrastructure.database.models.role import Role
from app.infrastructure.database.models.clinic import Clinic
from app.infrastructure.database.models.user_clinic_role import UserClinicRole
from app.infrastructure.database.models.department import Department
from app.infrastructure.database.models.employee import Employee
from app.infrastructure.database.models.doctor import Doctor
from app.infrastructure.database.models.patient import Patient
from app.infrastructure.database.models.appointment import Appointment
from app.infrastructure.database.models.work_queue import WorkQueue
from app.infrastructure.database.models.user_task import UserTask
from app.infrastructure.database.models.payment import Payment
from app.infrastructure.database.models.insurance import Insurance
from app.infrastructure.database.models.financial_transaction import FinancialTransaction
from app.infrastructure.database.models.salary_structure import SalaryStructure
from app.infrastructure.database.models.attendance import Attendance
from app.infrastructure.database.models.payroll import Payroll
from app.infrastructure.database.models.payslip import Payslip
from app.infrastructure.database.models.target import Target

# This is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the SQLAlchemy URL from our settings
config.set_main_option("sqlalchemy.url", settings.database_url)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    
    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.
    
    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    
    In this scenario we need to create an Engine and associate a connection
    with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
