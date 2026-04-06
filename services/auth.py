"""
Auth Service Module
-------------------
This module provides a comprehensive authentication and authorization service 
using JWT (JSON Web Tokens), password hashing with bcrypt, and Redis caching.
"""

from typing import Optional
from datetime import datetime, timedelta, UTC
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from database.db import get_db
from repository import users as repository_users
from config.config import settings
from services.cache import get_cached_user, cache_user
from database.models import User, UserRole

class Auth:
    """
    Handles password hashing, token generation, and user authentication.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    # Шлях, куди FastAPI буде відправляти клієнта для отримання токена
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

    def verify_password(self, plain_password, hashed_password):
        """
        Verifies if a plain password matches the stored hash.

        :param plain_password: The password provided by the user.
        :param hashed_password: The hashed password from the database.
        :return: True if match, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Generates a bcrypt hash from a plain password.

        :param password: Plain text password.
        :return: Hashed password string.
        """
        return self.pwd_context.hash(password)

    def create_email_token(self, data: dict):
        """
        Generates a token for email verification valid for 24 hours.

        :param data: Dictionary containing 'sub' (user email).
        :return: Encoded JWT token.
        """
        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(hours=24)
        to_encode.update({"iat": datetime.now(UTC), "exp": expire, "scope": "email_token"})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def get_email_from_token(self, token: str):
        """
        Decodes an email verification token and returns the email address.

        :param token: The JWT email token.
        :raises HTTPException: If token scope is invalid or expired.
        :return: The user email (sub).
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get("scope") != "email_token":
                raise HTTPException(status_code=400, detail="Invalid token scope")
            return payload.get("sub")
        except JWTError:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

    # Генерація Access Token
    def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Generates a JWT access token.

        :param data: Data to encode (usually user email).
        :param expires_delta: Optional expiration time in seconds.
        :return: Encoded JWT token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(UTC) + timedelta(minutes=15)
        to_encode.update({"iat": datetime.now(UTC), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    # Генерація Refresh Token (для оновлення access токена)
    def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Generates a JWT refresh token valid for 7 days by default.

        :param data: Data to encode.
        :param expires_delta: Optional expiration time.
        :return: Encoded JWT token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(UTC) + timedelta(days=7)
        to_encode.update({"iat": datetime.now(UTC), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    # Функція для отримання поточного користувача з JWT токена
    def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        Authenticates the current user via JWT.

        Checks Redis cache first. If not found, fetches from database and caches the result.

        :param token: The access token from the request header.
        :param db: The database session.
        :raises HTTPException: If credentials cannot be validated.
        :return: The User object.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get("scope") == "access_token":
                email = payload.get("sub")
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = get_cached_user(email)
        
        if user is None:
            print(f"[DB] Fetching user {email} from Database...")
            user = repository_users.get_user_by_email(email, db)
            
            if user is None:
                raise credentials_exception
            
            cache_user(user)
        else:
            print(f"[REDIS] Fetching user {email} from Cache!")
            
        return user

    def create_reset_token(self, email: str):
        """
        Generates a short-lived token (1 hour) for password reset.

        :param email: User email address.
        :return: Encoded JWT token.
        """
        expire = datetime.now(UTC) + timedelta(hours=1)
        to_encode = {"sub": email, "iat": datetime.now(UTC), "exp": expire, "scope": "password_reset"}
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def get_email_from_reset_token(self, token: str):
        """
        Decodes a password reset token.

        :param token: The reset JWT token.
        :return: User email.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get("scope") != "password_reset":
                raise HTTPException(status_code=400, detail="Invalid token scope")
            return payload.get("sub")
        except JWTError:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        
    def decode_access_token(self, token: str):
        """
        Generic JWT decoder.

        :param token: Any JWT token.
        :return: Payload dictionary if valid, else None.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except JWTError:
            return None
        
auth_service = Auth()

class RoleChecker:
    """
    Dependency to restrict access to specific user roles.
    """
    def __init__(self, allowed_roles: list[UserRole]):
        """
        Initializes the checker with a list of permitted roles.

        :param allowed_roles: List of UserRole enums.
        """
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(auth_service.get_current_user)):
        """
        Checks if the current user has one of the allowed roles.

        :param current_user: Authenticated user object.
        :raises HTTPException: 403 Forbidden if role is not allowed.
        :return: The validated user.
        """
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Operation not permitted"
            )
        return current_user

allow_admin = RoleChecker([UserRole.admin])