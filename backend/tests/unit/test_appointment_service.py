"""
Unit tests for Appointment Service.

Tests business logic without database dependencies.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.application.services.appointment_service import AppointmentService
from app.application.dto.appointment_dto import BookAppointmentDTO
from app.core.exceptions import ConflictError, ValidationError


@pytest.fixture
def mock_repositories():
    """Create mock repositories."""
    appointment_repo = AsyncMock()
    patient_repo = AsyncMock()
    doctor_repo = AsyncMock()
    department_repo = AsyncMock()
    
    return {
        "appointment_repo": appointment_repo,
        "patient_repo": patient_repo,
        "doctor_repo": doctor_repo,
        "department_repo": department_repo,
    }


@pytest.fixture
def appointment_service(mock_repositories, db_session):
    """Create AppointmentService instance with mocked dependencies."""
    service = AppointmentService(db_session)
    service.appointment_repository = mock_repositories["appointment_repo"]
    service.patient_repository = mock_repositories["patient_repo"]
    service.doctor_repository = mock_repositories["doctor_repo"]
    service.department_repository = mock_repositories["department_repo"]
    return service


@pytest.fixture
def sample_appointment_data():
    """Sample appointment booking data."""
    future_date = datetime.utcnow() + timedelta(days=1, hours=2)
    return BookAppointmentDTO(
        patient_id=uuid4(),
        doctor_id=uuid4(),
        department_id=uuid4(),
        appointment_date=future_date,
        duration_minutes=30,
        appointment_type="CONSULTATION",
        reason="Regular checkup",
    )


@pytest.mark.asyncio
async def test_book_appointment_success(
    appointment_service, sample_appointment_data, mock_repositories
):
    """Test successful appointment booking."""
    # Arrange
    mock_repositories["patient_repo"].get_by_id.return_value = MagicMock()
    mock_repositories["doctor_repo"].get_by_id.return_value = MagicMock()
    mock_repositories["department_repo"].get_by_id.return_value = MagicMock()
    mock_repositories["appointment_repo"].find_conflicting.return_value = None
    
    created_appointment = MagicMock()
    created_appointment.id = uuid4()
    mock_repositories["appointment_repo"].create.return_value = created_appointment
    
    # Act
    result = await appointment_service.book_appointment(sample_appointment_data)
    
    # Assert
    assert result is not None
    mock_repositories["appointment_repo"].create.assert_called_once()


@pytest.mark.asyncio
async def test_book_appointment_conflict(
    appointment_service, sample_appointment_data, mock_repositories
):
    """Test appointment booking with time conflict."""
    # Arrange
    mock_repositories["patient_repo"].get_by_id.return_value = MagicMock()
    mock_repositories["doctor_repo"].get_by_id.return_value = MagicMock()
    mock_repositories["department_repo"].get_by_id.return_value = MagicMock()
    
    # Simulate conflicting appointment
    conflicting = MagicMock()
    mock_repositories["appointment_repo"].find_conflicting.return_value = conflicting
    
    # Act & Assert
    with pytest.raises(ConflictError, match="conflict"):
        await appointment_service.book_appointment(sample_appointment_data)


@pytest.mark.asyncio
async def test_book_appointment_past_date(
    appointment_service, mock_repositories
):
    """Test appointment booking with past date."""
    # Arrange
    past_date = datetime.utcnow() - timedelta(days=1)
    appointment_data = BookAppointmentDTO(
        patient_id=uuid4(),
        doctor_id=uuid4(),
        department_id=uuid4(),
        appointment_date=past_date,
        duration_minutes=30,
    )
    
    # Act & Assert
    with pytest.raises(ValidationError, match="future"):
        await appointment_service.book_appointment(appointment_data)


@pytest.mark.asyncio
async def test_book_appointment_too_soon(
    appointment_service, mock_repositories
):
    """Test appointment booking less than 1 hour in advance."""
    # Arrange
    too_soon = datetime.utcnow() + timedelta(minutes=30)
    appointment_data = BookAppointmentDTO(
        patient_id=uuid4(),
        doctor_id=uuid4(),
        department_id=uuid4(),
        appointment_date=too_soon,
        duration_minutes=30,
    )
    
    mock_repositories["patient_repo"].get_by_id.return_value = MagicMock()
    mock_repositories["doctor_repo"].get_by_id.return_value = MagicMock()
    mock_repositories["department_repo"].get_by_id.return_value = MagicMock()
    
    # Act & Assert
    with pytest.raises(ValidationError, match="1 hour"):
        await appointment_service.book_appointment(appointment_data)
