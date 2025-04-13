from typing import List
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import Contact
from src.schemas import (
    ContactCreate,
    ContactUpdate,
    ContactModel,
    ContactUpdateBirthdate,
)


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(
        self,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ContactModel]:
        stmt = select(Contact)
        if first_name:
            stmt = stmt.where(Contact.first_name.ilike(f"%{first_name}%"))
        if last_name:
            stmt = stmt.where(Contact.last_name.ilike(f"%{last_name}%"))
        if email:
            stmt = stmt.where(Contact.email.ilike(f"%{email}%"))
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_contact_by_id(self, contact_id: int) -> ContactModel | None:
        stmt = select(Contact).where(Contact.id == contact_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_contact(self, contact: ContactCreate) -> ContactModel:
        new_contact = Contact(**contact.model_dump())
        self.db.add(new_contact)
        await self.db.commit()
        await self.db.refresh(new_contact)
        return await self.get_contact_by_id(new_contact.id)

    async def update_contact(
        self, contact_id: int, contact: ContactUpdate
    ) -> ContactModel | None:
        stmt = select(Contact).where(Contact.id == contact_id)
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
        self, contact_id: int, birthdate: ContactUpdateBirthdate
    ) -> ContactModel | None:
        stmt = select(Contact).where(Contact.id == contact_id)
        result = await self.db.execute(stmt)
        existing_contact = result.scalar_one_or_none()
        if existing_contact:
            existing_contact.birthdate = birthdate.birthdate
            await self.db.commit()
            await self.db.refresh(existing_contact)
            return existing_contact
        return None

    async def get_birthdays_next_week(self) -> List[ContactModel]:
        stmt = select(Contact).where(
            Contact.birthdate >= (datetime.now() + timedelta(days=1)).date(),
            Contact.birthdate <= (datetime.now() + timedelta(days=7)).date(),
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def delete_contact(self, contact_id: int) -> ContactModel | None:
        stmt = select(Contact).where(Contact.id == contact_id)
        result = await self.db.execute(stmt)
        existing_contact = result.scalar_one_or_none()
        if existing_contact:
            await self.db.delete(existing_contact)
            await self.db.commit()
            return existing_contact
        return None
