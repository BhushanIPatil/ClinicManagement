"""
Unit tests for Authentication Service.

Tests authentication logic including password hashing and token generation.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.application.services.auth_service import AuthService
from app.application.dto.auth_dto import LoginRequestDTO, RegisterRequestDTO
from app.core.exceptions import UnauthorizedError


@pytest.fixture
def auth_service(db_session):
    """Create AuthService instance."""
    return AuthService(db_session)


@pytest.fixture
def sample_register_data():
    """Sample registration data."""
    return RegisterRequestDTO(
        email="newuser@example.com",
        username="newuser",
        password="SecurePass123!",
        first_name="New",
        last_name="User",
        phone="+1234567890",
    )


@pytest.fixture
def sample_login_data():
    """Sample login data."""
    return LoginRequestDTO(
        username="testuser",
        password="TestPassword123!",
    )


@pytest.mark.asyncio
async def test_register_user_success(auth_service, sample_register_data, db_session):
    """Test successful user registration."""
    # Mock user repository
    with patch("app.application.services.auth_service.UserRepository") as mock_repo:
        mock_repo_instance = AsyncMock()
        mock_repo.return_value = mock_repo_instance
        
        # Mock user not exists
        mock_repo_instance.get_by_email.return_value = None
        mock_repo_instance.get_by_username.return_value = None
        
        # Mock user creation
        created_user = MagicMock()
        created_user.id = uuid4()
        created_user.email = sample_register_data.email
        created_user.username = sample_register_data.username
        created_user.is_active = True
        mock_repo_instance.create.return_value = created_user
        
        # Act
        result = await auth_service.register(sample_register_data)
        
        # Assert
        assert result is not None
        assert result.user.email == sample_register_data.email
        assert result.tokens.access_token is not None


@pytest.mark.asyncio
async def test_register_duplicate_email(auth_service, sample_register_data):
    """Test registration with duplicate email."""
    with patch("app.application.services.auth_service.UserRepository") as mock_repo:
        mock_repo_instance = AsyncMock()
        mock_repo.return_value = mock_repo_instance
        
        # Mock user exists
        existing_user = MagicMock()
        mock_repo_instance.get_by_email.return_value = existing_user
        
        # Act & Assert
        with pytest.raises(Exception):  # Should raise conflict error
            await auth_service.register(sample_register_data)


@pytest.mark.asyncio
async def test_login_success(auth_service, sample_login_data):
    """Test successful login."""
    with patch("app.application.services.auth_service.UserRepository") as mock_repo:
        mock_repo_instance = AsyncMock()
        mock_repo.return_value = mock_repo_instance
        
        # Mock user exists with correct password
        user = MagicMock()
        user.id = uuid4()
        user.email = "test@example.com"
        user.username = sample_login_data.username
        user.is_active = True
        user.hashed_password = "$2b$12$hashed"  # Mock hashed password
        
        mock_repo_instance.get_by_username_or_email.return_value = user
        
        # Mock password verification
        with patch("app.core.security.password.verify_password") as mock_verify:
            mock_verify.return_value = True
            
            # Act
            result = await auth_service.login(sample_login_data)
            
            # Assert
            assert result is not None
            assert result.tokens.access_token is not None


@pytest.mark.asyncio
async def test_login_invalid_credentials(auth_service, sample_login_data):
    """Test login with invalid credentials."""
    with patch("app.application.services.auth_service.UserRepository") as mock_repo:
        mock_repo_instance = AsyncMock()
        mock_repo.return_value = mock_repo_instance
        
        # Mock user not found
        mock_repo_instance.get_by_username_or_email.return_value = None
        
        # Act & Assert
        with pytest.raises(UnauthorizedError):
            await auth_service.login(sample_login_data)
