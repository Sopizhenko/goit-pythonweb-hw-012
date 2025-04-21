"""
Contact repository module for managing contact data in the database.
"""

from typing import List
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import Contact, User
from src.schemas import (
    ContactCreate,
    ContactUpdate,
    ContactModel,
    ContactUpdateBirthdate,
)


class ContactRepository:
    """
    Repository for managing contacts in the database.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.


        Args:
            session (AsyncSession): The database session to use.
        """
        self.db = session

    async def get_contacts(
        self,
        user: User,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ContactModel]:
        """
        Get a list of contacts for a user with optional filters.

        Args:
            user (User): The user for whom to retrieve contacts.
            first_name (str, optional): Filter by first name.
            last_name (str, optional): Filter by last name.
            email (str, optional): Filter by email.
            skip (int, optional): Number of records to skip.
            limit (int, optional): Maximum number of records to return.


        Returns:
            List[ContactModel]: A list of contacts matching the criteria.
        """

        stmt = select(Contact).where(Contact.user_id == user.id)
        if first_name:
            stmt = stmt.where(Contact.first_name.ilike(f"%{first_name}%"))
        if last_name:
            stmt = stmt.where(Contact.last_name.ilike(f"%{last_name}%"))
        if email:
            stmt = stmt.where(Contact.email.ilike(f"%{email}%"))
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_contact_by_id(
        self, contact_id: int, user: User
    ) -> ContactModel | None:
        """
        Get a contact by its ID for a specific user.
        
        Args:
            contact_id (int): The ID of the contact to retrieve.
            user (User): The user for whom to retrieve the contact.


        Returns:
            ContactModel | None: The contact if found, otherwise None.
        """
        stmt = select(Contact).where(
            Contact.id == contact_id, Contact.user_id == user.id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_contact(self, contact: ContactCreate, user: User) -> ContactModel:
        """
        Create a new contact for a specific user.

        Args:
            contact (ContactCreate): The contact data to create.
            user (User): The user for whom to create the contact.


        Returns:
            ContactModel: The created contact.
        """
        new_contact = Contact(**contact.model_dump())
        new_contact.user_id = user.id
        self.db.add(new_contact)
        await self.db.commit()
        await self.db.refresh(new_contact)
        return await self.get_contact_by_id(new_contact.id)

    async def update_contact(
        self, contact_id: int, contact: ContactUpdate, user: User
    ) -> ContactModel | None:
        """
        Update an existing contact for a specific user.

        Args:
            contact_id (int): The ID of the contact to update.
            contact (ContactUpdate): The updated contact data.
            user (User): The user for whom to update the contact.


        Returns:
            ContactModel | None: The updated contact if found, otherwise None.
        """
        stmt = select(Contact).where(
            Contact.id == contact_id, Contact.user_id == user.id
        )
        result = await self.db.execute(stmt)
        existing_contact = result.scalar_one_or_none()
        if existing_contact:
            for key, value in contact.model_dump(exclude_unset=True).items():
                setattr(existing_contact, key, value)
            await self.db.commit()
            await self.db.refresh(existing_contact)
            return existing_contact
        return None

    async def update_contact_birthdate(
        self, contact_id: int, birthdate: ContactUpdateBirthdate, user: User
    ) -> ContactModel | None:
        """
        Update the birthdate of an existing contact for a specific user.

        Args:
            contact_id (int): The ID of the contact to update.
            birthdate (ContactUpdateBirthdate): The updated birthdate data.
            user (User): The user for whom to update the contact.


        Returns:
            ContactModel | None: The updated contact if found, otherwise None.
        """
        stmt = select(Contact).where(
            Contact.id == contact_id, Contact.user_id == user.id
        )
        result = await self.db.execute(stmt)
        existing_contact = result.scalar_one_or_none()
        if existing_contact:
            existing_contact.birthdate = birthdate.birthdate
            await self.db.commit()
            await self.db.refresh(existing_contact)
            return existing_contact
        return None

    async def get_birthdays_next_week(self, user: User) -> List[ContactModel]:
        """
        Get a list of contacts with birthdays in the next week for a specific user.

        Args:
            user (User): The user for whom to retrieve contacts.


        Returns:
            List[ContactModel]: A list of contacts with birthdays in the next week.
        """
        stmt = select(Contact).where(
            Contact.birthdate >= (datetime.now() + timedelta(days=1)).date(),
            Contact.birthdate <= (datetime.now() + timedelta(days=7)).date(),
            Contact.user_id == user.id,
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def delete_contact(self, contact_id: int, user: User) -> ContactModel | None:
        """
        Delete a contact by its ID for a specific user.

        Args:
            contact_id (int): The ID of the contact to delete.
            user (User): The user for whom to delete the contact.


        Returns:
            ContactModel | None: The deleted contact if found, otherwise None.
        """
        stmt = select(Contact).where(
            Contact.id == contact_id, Contact.user_id == user.id
        )
        result = await self.db.execute(stmt)
        existing_contact = result.scalar_one_or_none()
        if existing_contact:
            await self.db.delete(existing_contact)
            await self.db.commit()
            return existing_contact
        return None
