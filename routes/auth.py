"""
Authentication Routes Module
----------------------------
This module defines the API endpoints for user authentication, including 
signup, login, email confirmation, and password reset flows.
"""

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi import Request

from database.db import get_db
from schemas.user import UserSchema, UserResponse, TokenSchema, ResetPassword, RequestResetEmail
from repository import users as repository_users
from services.auth import auth_service
from database.models import User
from services.limiter import limiter
from services.email import send_email, send_reset_password_email
from config.config import settings

router = APIRouter(prefix='/auth', tags=["auth"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, db: Session = Depends(get_db)):
    """
    Registers a new user in the system and sends a confirmation email.

    :param body: User registration data (username, email, password).
    :type body: UserSchema
    :param db: The database session.
    :type db: Session
    :raises HTTPException: 409 if the account already exists.
    :return: The created user information.
    :rtype: User
    """
    exist_user = repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    
    body.password = auth_service.get_password_hash(body.password)
    
    new_user = repository_users.create_user(body, db)
    
    host = settings.base_url
    await send_email(new_user.email, new_user.username, str(host))
    return new_user

@router.post("/login", response_model=TokenSchema)
def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticates a user and returns access and refresh tokens.

    Checks email existence, confirmation status, and password validity.

    :param body: OAuth2 compatible form containing username (email) and password.
    :type body: OAuth2PasswordRequestForm
    :param db: The database session.
    :type db: Session
    :raises HTTPException: 401 if credentials are invalid or email is not confirmed.
    :return: A dictionary containing access_token, refresh_token, and token_type.
    :rtype: dict
    """
    user = repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=401, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    
    access_token = auth_service.create_access_token(data={"sub": user.email})
    refresh_token = auth_service.create_refresh_token(data={"sub": user.email})
    
    repository_users.update_token(user, refresh_token, db)
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get("/me")
@limiter.limit("5/minute")
def me(
    request: Request,
    user: User = Depends(auth_service.get_current_user)
):
    """
    Returns the profile information of the currently authenticated user.

    This endpoint is rate-limited to 5 requests per minute.

    :param request: The incoming HTTP request (required for rate limiting).
    :type request: Request
    :param user: The current authenticated user obtained from the JWT token.
    :type user: User
    :return: The user profile object.
    :rtype: User
    """
    return user

@router.get("/confirm_email/{token}")
def confirm_email(token: str, db: Session = Depends(get_db)):
    """
    Confirms a user's email address using a verification token.

    :param token: The verification JWT token sent to the user's email.
    :type token: str
    :param db: The database session.
    :type db: Session
    :raises HTTPException: 400 if the token is invalid or user not found.
    :return: Success message.
    :rtype: dict
    """
    email = auth_service.get_email_from_token(token)
    user = repository_users.get_user_by_email(email, db)

    if user is None:
        raise HTTPException(status_code=400, detail="Verification error")
    if user.confirmed:
        return {"message": "Email already confirmed"}

    repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}

@router.post("/forgot_password")
async def forgot_password(
    body: RequestResetEmail, 
    background_tasks: BackgroundTasks, # Використовуйте BackgroundTasks для швидкості
    db: Session = Depends(get_db)
):
    """
    Initiates the password reset process by sending a reset link via email.

    This operation is performed as a background task to ensure quick API response.

    :param body: The user's email address to request a reset for.
    :type body: RequestResetEmail
    :param background_tasks: FastAPI background tasks manager.
    :type background_tasks: BackgroundTasks
    :param db: The database session.
    :type db: Session
    :return: A generic message indicating the email has been sent if the user exists.
    :rtype: dict
    """
    user = repository_users.get_user_by_email(body.email, db)
    if user:
        reset_token = auth_service.create_reset_token(user.email)
        host = settings.base_url 
        
        # Відправляємо лист у фоні, щоб не затримувати відповідь API
        background_tasks.add_task(
            send_reset_password_email, 
            user.email, 
            user.username, 
            str(host), 
            reset_token
        )
    
    return {"message": "If the account exists, a reset email has been sent."}

@router.post("/reset_password")
def reset_password(body: ResetPassword, db: Session = Depends(get_db)):
    """
    Resets the user's password using a valid reset token.

    :param body: Contains the reset token and the new password.
    :type body: ResetPassword
    :param db: The database session.
    :type db: Session
    :raises HTTPException: 404 if the user associated with the token is not found.
    :return: Success message.
    :rtype: dict
    """
    email = auth_service.get_email_from_reset_token(body.token)
    hashed_password = auth_service.get_password_hash(body.new_password)
    
    user = repository_users.update_password(email, hashed_password, db)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {"message": "Password updated successfully"}