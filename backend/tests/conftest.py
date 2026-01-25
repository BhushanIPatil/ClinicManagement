"""
Pytest configuration and fixtures for backend tests.
"""

import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.core.config import settings

# Test database URL (SQLite in-memory for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session for each test.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    """
    Create a test client for API tests.
    """
    from fastapi.testclient import TestClient
    from app.main import app
    
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture
def sample_patient_data():
    """Sample patient data for testing."""
    return {
        "patient_number": "PAT001",
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1990-01-15",
        "gender": "MALE",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
    }
