from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import (
    ContactModel,
    ContactCreate,
    ContactUpdate,
    ContactUpdateBirthdate,
)
from src.services.contacts import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get(
    "/",
    response_model=List[ContactModel],
    status_code=status.HTTP_200_OK,
)
async def get_contacts(
    first_name: str = None,
    last_name: str = None,
    email: str = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> List[ContactModel]:
    service = ContactService(db)
    contacts = await service.get_contacts(first_name, last_name, email, skip, limit)
    return contacts


@router.get("/birthdays_next_week", response_model=List[ContactModel])
async def get_birthdays_next_week(
    db: AsyncSession = Depends(get_db),
) -> List[ContactModel]:
    service = ContactService(db)
    return await service.get_birthdays_next_week()


@router.get("/{contact_id}", response_model=ContactModel)
async def get_contact_by_id(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
) -> ContactModel:
    service = ContactService(db)
    contact = await service.get_contact_by_id(contact_id)
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
) -> ContactModel:
    service = ContactService(db)
    return await service.create_contact(contact)


@router.put("/{contact_id}", response_model=ContactUpdate)
async def update_contact(
    contact_id: int,
    contact: ContactUpdate,
    db: AsyncSession = Depends(get_db),
) -> ContactModel:
    service = ContactService(db)
    updated_contact = await service.update_contact(contact_id, contact)
    if not updated_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated_contact


@router.patch("/{contact_id}/birthdate", response_model=ContactModel)
async def update_contact_birthdate(
    contact_id: int,
    birthdate: ContactUpdateBirthdate,
    db: AsyncSession = Depends(get_db),
) -> ContactModel:
    service = ContactService(db)
    updated_contact = await service.update_contact_birthdate(contact_id, birthdate)
    if not updated_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated_contact


@router.delete("/{contact_id}", response_model=ContactModel)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
) -> ContactModel:
    service = ContactService(db)
    deleted_contact = await service.delete_contact(contact_id)
    if not deleted_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return deleted_contact
