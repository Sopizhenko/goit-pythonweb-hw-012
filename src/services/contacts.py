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
    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactCreate, user: User) -> ContactModel:
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
        return await self.repository.get_contacts(
            user, first_name, last_name, email, skip, limit
        )

    async def get_contact_by_id(
        self, contact_id: int, user: User
    ) -> ContactModel | None:
        return await self.repository.get_contact_by_id(contact_id, user)

    async def update_contact(
        self, contact_id: int, body: ContactUpdate, user: User
    ) -> ContactModel | None:
        return await self.repository.update_contact(contact_id, body, user)

    async def update_contact_birthdate(
        self, contact_id: int, body: ContactUpdateBirthdate, user: User
    ) -> ContactModel | None:
        return await self.repository.update_contact_birthdate(contact_id, body, user)

    async def delete_contact(self, contact_id: int, user: User) -> ContactModel | None:
        return await self.repository.delete_contact(contact_id, user)

    async def get_birthdays_next_week(self, user: User) -> list[ContactModel]:
        return await self.repository.get_birthdays_next_week(user)
