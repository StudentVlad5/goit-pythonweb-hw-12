"""
Database Models Module
----------------------
This module defines the SQLAlchemy ORM models for the application, 
including the User and Contact entities and their relationships.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, DateTime, func
from sqlalchemy.orm import relationship, DeclarativeBase
import enum
from sqlalchemy import Enum

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models in the application.
    Uses DeclarativeBase from SQLAlchemy 2.x.
    """
    pass

class UserRole(enum.Enum):
    """
    Enumeration of available user roles within the system.
    
    Attributes:
        admin: Full access to the system.
        user: Standard access to personal contacts.
    """
    admin = "admin"
    user = "user"

class User(Base):
    """
    ORM model representing a user of the application.

    Attributes:
        id (int): Primary key for the user.
        username (str): The display name of the user.
        email (str): Unique email address, used for authentication.
        password (str): Hashed password string.
        avatar (str, optional): URL to the user's avatar image.
        refresh_token (str, optional): Token used to refresh the session.
        confirmed (bool): Flag indicating if the email has been verified.
        created_at (datetime): Timestamp of when the account was created.
        role (UserRole): Role assigned to the user (defaults to 'user').
        contacts (list): Relationship back-reference to the user's contacts.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    role = Column(Enum(UserRole), default=UserRole.user)

class Contact(Base):
    """
    ORM model representing a contact entry in a user's address book.

    Attributes:
        id (int): Primary key for the contact.
        first_name (str): The contact's first name.
        last_name (str): The contact's last name.
        email (str): Unique email address for the contact.
        phone (str): Phone number of the contact.
        birthday (date): Date of birth of the contact.
        additional_data (str, optional): Miscellaneous notes about the contact.
        user_id (int): Foreign key linking to the owner of the contact.
        user (User): Relationship object to the User model.
    """
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20))
    birthday = Column(Date)
    additional_data = Column(String(250), nullable=True)
    
    # Зв'язок з користувачем
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    user = relationship("User", backref="contacts")