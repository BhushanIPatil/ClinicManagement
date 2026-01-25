"""
API Integration tests for Authentication endpoints.
"""

import pytest
from fastapi.testclient import TestClient


def test_register_user_success(client, sample_user_data):
    """Test successful user registration via API."""
    response = client.post("/api/v1/auth/register", json=sample_user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert "user" in data
    assert "tokens" in data
    assert data["user"]["email"] == sample_user_data["email"]
    assert data["tokens"]["access_token"] is not None


def test_register_duplicate_email(client, sample_user_data):
    """Test registration with duplicate email."""
    # Register first time
    client.post("/api/v1/auth/register", json=sample_user_data)
    
    # Try to register again
    response = client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 409  # Conflict


def test_login_success(client, sample_user_data):
    """Test successful login via API."""
    # Register user first
    client.post("/api/v1/auth/register", json=sample_user_data)
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"],
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "tokens" in data
    assert data["tokens"]["access_token"] is not None


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "nonexistent", "password": "wrong"},
    )
    
    assert response.status_code == 401


def test_get_current_user_requires_auth(client):
    """Test that getting current user requires authentication."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_current_user_success(client, sample_user_data):
    """Test getting current user with valid token."""
    # Register and login
    register_response = client.post("/api/v1/auth/register", json=sample_user_data)
    tokens = register_response.json()["tokens"]
    
    # Get current user
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == sample_user_data["email"]
