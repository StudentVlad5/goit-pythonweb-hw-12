"""
User Schemas Module
-------------------
This module defines Pydantic models for user-related data validation, 
authentication tokens, and password reset requests.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from database.models import UserRole

class RequestResetEmail(BaseModel):
    """
    Schema for requesting a password reset email.
    
    Attributes:
        email (EmailStr): The email address where the reset link will be sent.
    """
    email: EmailStr

class ResetPassword(BaseModel):
    """
    Schema for setting a new password using a reset token.
    
    Attributes:
        token (str): The verification token received via email.
        new_password (str): The new password (6-255 characters).
    """
    token: str
    new_password: str = Field(min_length=6, max_length=255)

class UserSchema(BaseModel):
    """
    Schema for user registration (Input).
    
    Attributes:
        username (str): Desired display name (3-50 characters).
        email (EmailStr): Valid email address for the account.
        password (str): Raw password string (6-255 characters).
    """
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=255)

class UserResponse(BaseModel):
    """
    Schema for user data returned in API responses (Output).
    
    Attributes:
        id (int): Database primary key.
        username (str): The user's display name.
        email (EmailStr): The user's email address.
        avatar (Optional[str]): URL to the user's avatar image.
        role (UserRole): Access level assigned to the user.
        confirmed (bool): Whether the email address has been verified.
        created_at (datetime): The timestamp of account creation.
    """
    id: int
    username: str
    email: EmailStr
    avatar: Optional[str]
    role: UserRole
    confirmed: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True) # Дозволяє працювати з об'єктами SQLAlchemy

class TokenSchema(BaseModel):
    """
    Schema for authentication tokens returned after login.
    
    Attributes:
        access_token (str): JWT access token for API authorization.
        refresh_token (str): Token used to obtain a new access token.
        token_type (str): Type of the token, defaults to 'bearer'.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RequestEmail(BaseModel):
    """
    Simple schema for operations requiring only an email address.
    
    Attributes:
        email (EmailStr): The targeted email address.
    """
    email: EmailStr