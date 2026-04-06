import os
import sys
import pytest
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport

# Встановлюємо заглушки ДО імпорту main
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_USER"] = "test"
os.environ["DB_PASSWORD"] = "test"
os.environ["DB_NAME"] = "test"
os.environ["SECRET_KEY"] = "test_secret"
os.environ["ALGORITHM"] = "HS256"
os.environ["MAIL_USERNAME"] = "test@test.com"
os.environ["MAIL_PASSWORD"] = "test"
os.environ["MAIL_FROM"] = "test@test.com"
os.environ["MAIL_PORT"] = "587"
os.environ["MAIL_SERVER"] = "localhost"
os.environ["CLOUDINARY_NAME"] = "test"
os.environ["CLOUDINARY_API_KEY"] = "test"
os.environ["CLOUDINARY_API_SECRET"] = "test"
os.environ["BASE_URL"] = "http://localhost:8000"

from main import app
from database.db import get_db, Base

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
async def client(db):
    """Створюємо асинхронний клієнт для тестів."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    
    # Новий спосіб передачі app в AsyncClient через transport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # Очищуємо overrides після тестів
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    mock_r = MagicMock()
    # Переконайтеся, що шлях 'services.cache.r' правильний для вашого проекту
    monkeypatch.setattr("services.cache.r", mock_r)
    return mock_r