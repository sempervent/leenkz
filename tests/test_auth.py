"""Tests for authentication functionality."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from leenkz.api.main import app
from leenkz.core.auth import get_password_hash
from leenkz.core.database import AsyncSessionLocal, User


@pytest.fixture
async def test_user():
    """Create a test user."""
    async with AsyncSessionLocal() as session:
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("testpass123"),
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest.mark.asyncio
async def test_register():
    """Test user registration."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "new@example.com",
                "username": "newuser",
                "password": "newpass123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "new@example.com"
        assert data["username"] == "newuser"
        assert "password" not in data


@pytest.mark.asyncio
async def test_login(test_user):
    """Test user login."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpass123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "wrong@example.com",
                "password": "wrongpass",
            },
        )
        assert response.status_code == 401 