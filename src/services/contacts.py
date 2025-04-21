"""
Contact service module for managing contact-related business logic.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.database.models import User
from src.schemas import (
    ContactModel,
    ContactCreate,
    ContactUpdate,
    ContactUpdateBirthdate,
)


class ContactService:
    """
    Service class for handling contact-related business logic.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the service with a database session.

        Args:
            db (AsyncSession): The database session to use.
        """
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactCreate, user: User) -> ContactModel:
        """
        Create a new contact for a user.

        Args:
            body (ContactCreate): The contact data for creating a new contact.
            user (User): The user who owns the contact.

        Returns:
            ContactModel: The created contact.
        """
        return await self.repository.create_contact(body, user)

    async def get_contacts(
        self,
        user: User,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ContactModel]:
        """
        Retrieve a list of contacts for a user with optional filters.

        Args:
            user (User): The user whose contacts to retrieve.
            first_name (str, optional): Filter by first name.
            last_name (str, optional): Filter by last name.
            email (str, optional): Filter by email address.
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            list[ContactModel]: List of contacts matching the criteria.
        """
        return await self.repository.get_contacts(
            user, first_name, last_name, email, skip, limit
        )

    async def get_contact_by_id(
        self, contact_id: int, user: User
    ) -> ContactModel | None:
        """
        Retrieve a specific contact by ID for a user.

        Args:
            contact_id (int): The ID of the contact to retrieve.
            user (User): The user who owns the contact.

        Returns:
            ContactModel | None: The contact if found, otherwise None.
        """
        return await self.repository.get_contact_by_id(contact_id, user)

    async def update_contact(
        self, contact_id: int, body: ContactUpdate, user: User
    ) -> ContactModel | None:
        """
        Update an existing contact for a user.

        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactUpdate): The updated contact data.
            user (User): The user who owns the contact.

        Returns:
            ContactModel | None: The updated contact if found, otherwise None.
        """
        return await self.repository.update_contact(contact_id, body, user)

    async def update_contact_birthdate(
        self, contact_id: int, body: ContactUpdateBirthdate, user: User
    ) -> ContactModel | None:
        """
        Update the birthdate of an existing contact.

        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactUpdateBirthdate): The updated birthdate data.
            user (User): The user who owns the contact.

        Returns:
            ContactModel | None: The updated contact if found, otherwise None.
        """
        return await self.repository.update_contact_birthdate(contact_id, body, user)

    async def delete_contact(self, contact_id: int, user: User) -> ContactModel | None:
        """
        Delete a contact for a user.

        Args:
            contact_id (int): The ID of the contact to delete.
            user (User): The user who owns the contact.

        Returns:
            ContactModel | None: The deleted contact if found, otherwise None.
        """
        return await self.repository.delete_contact(contact_id, user)

    async def get_birthdays_next_week(self, user: User) -> list[ContactModel]:
        """
        Get a list of contacts who have birthdays in the next week.

        Args:
            user (User): The user whose contacts to check.

        Returns:
            list[ContactModel]: List of contacts with birthdays in the next week.
        """
        return await self.repository.get_birthdays_next_week(user)
