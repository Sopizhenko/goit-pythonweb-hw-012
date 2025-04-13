from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas import (
    ContactModel,
    ContactCreate,
    ContactUpdate,
    ContactUpdateBirthdate,
)


class ContactService:
    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactCreate) -> ContactModel:
        return await self.repository.create_contact(body)

    async def get_contacts(
        self,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ContactModel]:
        return await self.repository.get_contacts(
            first_name, last_name, email, skip, limit
        )

    async def get_contact_by_id(self, contact_id: int) -> ContactModel | None:
        return await self.repository.get_contact_by_id(contact_id)

    async def update_contact(
        self, contact_id: int, body: ContactUpdate
    ) -> ContactModel | None:
        return await self.repository.update_contact(contact_id, body)

    async def update_contact_birthdate(
        self, contact_id: int, body: ContactUpdateBirthdate
    ) -> ContactModel | None:
        return await self.repository.update_contact_birthdate(contact_id, body)

    async def delete_contact(self, contact_id: int) -> ContactModel | None:
        return await self.repository.delete_contact(contact_id)

    async def get_birthdays_next_week(self) -> list[ContactModel]:
        return await self.repository.get_birthdays_next_week()
