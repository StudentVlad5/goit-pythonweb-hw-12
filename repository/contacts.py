"""
Contacts Repository Module
--------------------------
This module contains the CRUD (Create, Read, Update, Delete) operations 
for managing contacts in the database, ensuring each user only accesses their own data.
"""

from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from database.models import Contact, User
from schemas.contact import ContactCreate, ContactUpdate

def get_contacts(name: str, last_name: str, email: str, user: User, db: Session) -> List[Contact]:
    """
    Retrieves a list of contacts for a specific user with optional filters.

    :param name: Optional filter by first name (case-insensitive partial match).
    :type name: str
    :param last_name: Optional filter by last name (case-insensitive partial match).
    :type last_name: str
    :param email: Optional filter by email address (case-insensitive partial match).
    :type email: str
    :param user: The owner of the contacts.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts that match the criteria.
    :rtype: List[Contact]
    """
    query = db.query(Contact).filter(Contact.user_id == user.id)
    if name:
        query = query.filter(Contact.first_name.ilike(f"%{name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))
    return query.all()

def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    """
    Retrieves a single contact by its ID for a specific user.

    :param contact_id: The unique identifier of the contact.
    :type contact_id: int
    :param user: The owner of the contact.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The contact object if found and owned by the user, otherwise None.
    :rtype: Contact | None
    """
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()

def create_contact(body: ContactCreate, user: User, db: Session) -> Contact:
    """
    Creates a new contact associated with a specific user.

    :param body: The data for the new contact.
    :type body: ContactCreate
    :param user: The user who will own this contact.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The newly created contact.
    :rtype: Contact
    """
    contact = Contact(**body.model_dump(), user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def remove_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    """
    Deletes a specific contact from the database for a given user.

    :param contact_id: The ID of the contact to be removed.
    :type contact_id: int
    :param user: The owner of the contact.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The removed contact if successful, otherwise None.
    :rtype: Contact | None
    """
    contact = get_contact(contact_id, user, db)  
    if contact:
        db.delete(contact)
        db.commit()
    return contact

def update_contact(contact_id: int, body: ContactUpdate, user: User, db: Session) -> Contact | None:
    """
    Updates an existing contact's information for a specific user.

    Only updates the fields provided in the body (exclude_unset=True).

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param body: The updated contact data.
    :type body: ContactUpdate
    :param user: The owner of the contact.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The updated contact if found, otherwise None.
    :rtype: Contact | None
    """
    contact = get_contact(contact_id, user, db) 
    if contact:
        # exclude_unset=True допоможе не затерти дані пустими значеннями
        for key, value in body.model_dump(exclude_unset=True).items():
            setattr(contact, key, value)
        db.commit()
        db.refresh(contact)
    return contact