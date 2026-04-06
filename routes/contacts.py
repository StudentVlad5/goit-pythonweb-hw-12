"""
Contacts Routes Module
----------------------
This module defines the API endpoints for managing contacts, including 
creation, retrieval with filtering, updating, and deletion. All operations 
are scoped to the currently authenticated user.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import User
from schemas.contact import ContactCreate, ContactUpdate, ContactResponse
from repository import contacts as repository_contacts
from services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
def read_contacts(
    name: str = Query(None),
    last_name: str = Query(None),
    email: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Retrieves a list of contacts for the authenticated user.
    
    Supports optional filtering by first name, last name, or email.

    :param name: Filter contacts by first name (optional).
    :type name: str
    :param last_name: Filter contacts by last name (optional).
    :type last_name: str
    :param email: Filter contacts by email (optional).
    :type email: str
    :param db: The database session.
    :type db: Session
    :param current_user: The currently authenticated user.
    :type current_user: User
    :return: A list of contacts matching the search criteria.
    :rtype: List[ContactResponse]
    """
    contacts = repository_contacts.get_contacts(name, last_name, email, current_user, db)
    return contacts


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    body: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Creates a new contact for the authenticated user.

    :param body: The data for the new contact.
    :type body: ContactCreate
    :param db: The database session.
    :type db: Session
    :param current_user: The currently authenticated user.
    :type current_user: User
    :return: The newly created contact.
    :rtype: ContactResponse
    """
    return repository_contacts.create_contact(body, current_user, db)


@router.get("/{contact_id}", response_model=ContactResponse)
def read_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Retrieves a specific contact by its unique ID.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The currently authenticated user.
    :type current_user: User
    :raises HTTPException: 404 if the contact is not found or doesn't belong to the user.
    :return: The requested contact.
    :rtype: ContactResponse
    """
    contact = repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: int,
    body: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Updates the information of an existing contact.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param body: The updated data for the contact.
    :type body: ContactUpdate
    :param db: The database session.
    :type db: Session
    :param current_user: The currently authenticated user.
    :type current_user: User
    :raises HTTPException: 404 if the contact is not found.
    :return: The updated contact.
    :rtype: ContactResponse
    """
    contact = repository_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Deletes a specific contact from the database.

    :param contact_id: The ID of the contact to delete.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The currently authenticated user.
    :type current_user: User
    :raises HTTPException: 404 if the contact is not found.
    :return: None (HTTP 204 status code).
    :rtype: None
    """
    contact = repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return None