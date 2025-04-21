"""
Contacts API module for managing contact-related endpoints.
"""

from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import (
    ContactModel,
    ContactCreate,
    ContactUpdate,
    ContactUpdateBirthdate,
)
from src.services.contacts import ContactService
from src.services.auth import get_current_user
from src.services.redis_cache import cache_response, redis_cache

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get(
    "/",
    response_model=List[ContactModel],
    status_code=status.HTTP_200_OK,
)
@cache_response(expire=300)  # Cache for 5 minutes
async def get_contacts(
    request: Request,
    first_name: str = None,
    last_name: str = None,
    email: str = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: str = Depends(get_current_user),
) -> List[ContactModel]:
    """
    Retrieve a list of contacts with optional filtering.

    Args:
        request (Request): The incoming request object.
        first_name (str, optional): Filter contacts by first name.
        last_name (str, optional): Filter contacts by last name.
        email (str, optional): Filter contacts by email.
        skip (int, optional): Number of records to skip. Defaults to 0.
        limit (int, optional): Maximum number of records to return. Defaults to 100.
        db (AsyncSession): Database session.
        user (str): Current authenticated user.

    Returns:
        List[ContactModel]: List of contacts matching the criteria.

    Note:
        Results are cached for 5 minutes per user and query parameters.
    """
    service = ContactService(db)
    contacts = await service.get_contacts(
        user, first_name, last_name, email, skip, limit
    )
    return contacts


@router.get("/birthdays_next_week", response_model=List[ContactModel])
@cache_response(expire=3600)  # Cache for 1 hour
async def get_birthdays_next_week(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: str = Depends(get_current_user),
) -> List[ContactModel]:
    """
    Retrieve contacts with birthdays in the next week.

    Args:
        request (Request): The incoming request object.
        db (AsyncSession): Database session.
        user (str): Current authenticated user.

    Returns:
        List[ContactModel]: List of contacts with birthdays in the next week.

    Note:
        Results are cached for 1 hour per user.
    """
    service = ContactService(db)
    return await service.get_birthdays_next_week(user)


@router.get("/{contact_id}", response_model=ContactModel)
@cache_response(expire=300)  # Cache for 5 minutes
async def get_contact_by_id(
    request: Request,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: str = Depends(get_current_user),
) -> ContactModel:
    """
    Retrieve a specific contact by ID.

    Args:
        request (Request): The incoming request object.
        contact_id (int): The ID of the contact to retrieve.
        db (AsyncSession): Database session.
        user (str): Current authenticated user.

    Returns:
        ContactModel: The requested contact.

    Raises:
        HTTPException: If the contact is not found.

    Note:
        Results are cached for 5 minutes per user and contact ID.
    """
    service = ContactService(db)
    contact = await service.get_contact_by_id(contact_id, user)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.post(
    "/",
    response_model=ContactModel,
    status_code=status.HTTP_201_CREATED,
)
async def create_contact(
    contact: ContactCreate,
    db: AsyncSession = Depends(get_db),
    user: str = Depends(get_current_user),
) -> ContactModel:
    """
    Create a new contact.

    Args:
        contact (ContactCreate): The contact data to create.
        db (AsyncSession): Database session.
        user (str): Current authenticated user.

    Returns:
        ContactModel: The created contact.
    """
    service = ContactService(db)
    new_contact = await service.create_contact(contact, user)
    # Clear user's contacts cache after creation
    await redis_cache.clear_user_cache(user.id)
    return new_contact


@router.put("/{contact_id}", response_model=ContactUpdate)
async def update_contact(
    contact_id: int,
    contact: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    user: str = Depends(get_current_user),
) -> ContactModel:
    """
    Update an existing contact.

    Args:
        contact_id (int): The ID of the contact to update.
        contact (ContactUpdate): The updated contact data.
        db (AsyncSession): Database session.
        user (str): Current authenticated user.

    Returns:
        ContactModel: The updated contact.

    Raises:
        HTTPException: If the contact is not found.
    """
    service = ContactService(db)
    updated_contact = await service.update_contact(contact_id, contact, user)
    if not updated_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    # Clear user's contacts cache after update
    await redis_cache.clear_user_cache(user.id)
    return updated_contact


@router.patch("/{contact_id}/birthdate", response_model=ContactModel)
async def update_contact_birthdate(
    contact_id: int,
    birthdate: ContactUpdateBirthdate,
    db: AsyncSession = Depends(get_db),
    user: str = Depends(get_current_user),
) -> ContactModel:
    """
    Update the birthdate of an existing contact.

    Args:
        contact_id (int): The ID of the contact to update.
        birthdate (ContactUpdateBirthdate): The new birthdate data.
        db (AsyncSession): Database session.
        user (str): Current authenticated user.

    Returns:
        ContactModel: The updated contact.

    Raises:
        HTTPException: If the contact is not found.
    """
    service = ContactService(db)
    updated_contact = await service.update_contact_birthdate(
        contact_id, birthdate, user
    )
    if not updated_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    # Clear user's contacts cache after birthdate update
    await redis_cache.clear_user_cache(user.id)
    return updated_contact


@router.delete("/{contact_id}", response_model=ContactModel)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: str = Depends(get_current_user),
) -> ContactModel:
    """
    Delete a contact.

    Args:
        contact_id (int): The ID of the contact to delete.
        db (AsyncSession): Database session.
        user (str): Current authenticated user.

    Returns:
        ContactModel: The deleted contact.

    Raises:
        HTTPException: If the contact is not found.
    """
    service = ContactService(db)
    deleted_contact = await service.delete_contact(contact_id, user)
    if not deleted_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    # Clear user's contacts cache after deletion
    await redis_cache.clear_user_cache(user.id)
    return deleted_contact
