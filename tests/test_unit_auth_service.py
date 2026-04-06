import pytest
from services.auth import auth_service
from fastapi import HTTPException
from database.models import User
from unittest.mock import AsyncMock, patch


def test_password_hashing():
    password = "secret_password"
    hashed = auth_service.get_password_hash(password)
    assert hashed != password
    assert auth_service.verify_password(password, hashed) is True

def test_create_access_token():
    data = {"sub": "test@example.com"}
    token = auth_service.create_access_token(data)
    assert isinstance(token, str)
    payload = auth_service.decode_access_token(token) # якщо у вас є такий метод
    assert payload["sub"] == "test@example.com"

@pytest.mark.asyncio
async def test_get_current_user_valid_token(db, mock_redis):
    email = "test@example.com"
    token = auth_service.create_access_token(data={"sub": email})
    mock_redis.get.return_value = None

    test_user = User(id=1, email=email, username="testuser")
    
    # Використовуємо AsyncMock, бо функція викликається з await
    with patch("repository.users.get_user_by_email", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = test_user
        
        # Також мокаємо cache_user, щоб не було PicklingError
        with patch("services.auth.cache_user") as mock_cache:
            user = await auth_service.get_current_user(token, db)
            
            assert user.email == email
            mock_get.assert_called_once()
@pytest.mark.asyncio
async def test_get_current_user_invalid_scope(db):
    token = auth_service.create_email_token({"sub": "test@test.com"})
    
    with pytest.raises(HTTPException) as exc:
        await auth_service.get_current_user(token, db)
    
    assert exc.value.status_code == 401

def test_create_password_reset_token():
    email = "vlad@example.com"
    token = auth_service.create_reset_token(email) 
    assert isinstance(token, str)
    
    payload = auth_service.get_email_from_reset_token(token)
    assert payload == email