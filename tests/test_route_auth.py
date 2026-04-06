import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_signup_user(client):
    response = await client.post(
        "/api/auth/signup",
        json={"username": "newuser", "email": "new@example.com", "password": "password123"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"

@pytest.mark.asyncio
async def test_login_user_not_confirmed(client):
    # Користувач існує, але email не підтверджено
    response = await client.post(
        "/api/auth/login",
        data={"username": "new@example.com", "password": "password123"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Email not confirmed"