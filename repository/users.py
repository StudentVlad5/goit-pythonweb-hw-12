"""
Users Repository Module
-----------------------
This module handles database operations for the User model, including
registration, email confirmation, and profile updates.
"""

from sqlalchemy.orm import Session
from database.models import User
from schemas.user import UserSchema

def get_user_by_email(email: str, db: Session) -> User:
    """
    Retrieves a user from the database based on their unique email address.

    :param email: The email address to search for.
    :type email: str
    :param db: The active database session.
    :type db: Session
    :return: The User object if found, otherwise None.
    :rtype: User | None
    """
    return db.query(User).filter(User.email == email).first()

def create_user(body: UserSchema, db: Session) -> User:
    """
    Creates a new user record in the database.

    :param body: The validated user data (from UserSchema).
    :type body: UserSchema
    :param db: The active database session.
    :type db: Session
    :return: The newly created User object with its assigned ID.
    :rtype: User
    """
    new_user = User(**body.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Updates the refresh token stored in the database for a specific user.

    :param user: The user instance to update.
    :type user: User
    :param token: The new refresh token string or None to clear it.
    :type token: str | None
    :param db: The active database session.
    :type db: Session
    :return: None
    """
    user.refresh_token = token
    db.commit()

def confirmed_email(email: str, db: Session) -> None:
    """
    Marks a user's email as verified in the database.

    :param email: The email address of the user who confirmed their registration.
    :type email: str
    :param db: The active database session.
    :type db: Session
    :return: None
    """
    user = get_user_by_email(email, db)
    user.confirmed = True
    db.commit()

def update_avatar(email: str, url: str, db: Session) -> User:
    """
    Updates the avatar image URL for a specific user.

    :param email: The email of the user to update.
    :type email: str
    :param url: The public URL of the uploaded avatar (e.g., from Cloudinary).
    :type url: str
    :param db: The active database session.
    :type db: Session
    :return: The updated User object.
    :rtype: User
    """
    user = get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user

def update_password(email: str, hashed_password: str, db: Session):
    """
    Updates a user's password in the database.

    This function is typically used during the "forgot password" flow.

    :param email: The email address identifying the user.
    :type email: str
    :param hashed_password: The new pre-hashed password.
    :type hashed_password: str
    :param db: The active database session.
    :type db: Session
    :return: The User object if the password was updated, otherwise None.
    :rtype: User | None
    """
    user = get_user_by_email(email, db)
    if user:
        user.password = hashed_password
        db.commit()
    return user