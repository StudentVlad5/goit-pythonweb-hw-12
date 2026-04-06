"""
Contact Schemas Module
----------------------
This module defines Pydantic models for data validation and serialization 
of contact entities. It ensures consistent data structures for creating, 
updating, and retrieving contacts.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import date
from typing import Optional

class ContactBase(BaseModel):
    """
    Base schema for contact data.
    
    Attributes:
        first_name (str): The first name of the contact (max 50 chars).
        last_name (str): The last name of the contact (max 50 chars).
        email (EmailStr): Validated email address.
        phone (str): Contact phone number (max 20 chars).
        birthday (date): Date of birth of the contact.
        additional_data (Optional[str]): Optional notes or extra info (max 250 chars).
    """
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: EmailStr
    phone: str = Field(max_length=20)
    birthday: date
    additional_data: Optional[str] = Field(None, max_length=250)

class ContactCreate(ContactBase):
    """
    Schema for creating a new contact. Inherits all fields from ContactBase.
    """
    pass

class ContactUpdate(ContactBase):
    """
    Schema for updating an existing contact. Inherits all fields from ContactBase.
    """
    pass

class ContactResponse(ContactBase):
    """
    Schema for the contact data returned in API responses.
    
    Includes the database ID and handles conversion from SQLAlchemy models.

    Attributes:
        id (int): The unique identifier from the database.
    """
    id: int
   
    model_config = ConfigDict(from_attributes=True)