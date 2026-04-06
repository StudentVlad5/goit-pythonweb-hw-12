"""
Users Routes Module
-------------------
This module defines the API endpoints for user profile management, 
specifically handling avatar uploads via Cloudinary integration.
"""
from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import User
from schemas.user import UserResponse
from services.auth import allow_admin
from services.cloudinary import cloudinary_service
from repository import users as repository_users

router = APIRouter(prefix="/users", tags=["users"])

@router.patch('/avatar', response_model=UserResponse)
def update_avatar_user(
    file: UploadFile = File(), 
    current_user: User = Depends(allow_admin),
    db: Session = Depends(get_db)
):
    """
    Updates the avatar for the currently authenticated administrator.

    The image is uploaded to Cloudinary, and the resulting URL is stored 
    in the user's database record.

    :param file: The image file to be uploaded.
    :type file: UploadFile
    :param current_user: The currently authenticated user (must have admin role).
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: The updated user profile with the new avatar URL.
    :rtype: User
    """
    public_id = f"ContactsApp/{current_user.username}"
    url = cloudinary_service.upload_image(file.file, public_id)
    user = repository_users.update_avatar(current_user.email, url, db)
    return user