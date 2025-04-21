"""
User repository module for managing user data in the database.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserCreate


class UserRepository:
    """
    Repository for managing users in the database.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.

        Args:
            session (AsyncSession): The database session to use.
        """
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Get a user by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Get a user by their username.

        Args:
            username (str): The username of the user to retrieve.

        Returns:
            User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Get a user by their email address.

        Args:
            email (str): The email address of the user to retrieve.

        Returns:
            User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Create a new user.

        Args:
            body (UserCreate): The user data to create.
            avatar (str, optional): The URL of the user's avatar image.

        Returns:
            User: The created user.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: str) -> None:
        """
        Mark a user's email as confirmed.

        Args:
            email (str): The email address of the user to confirm.
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Update a user's avatar URL.

        Args:
            email (str): The email address of the user to update.
            url (str): The new avatar URL.

        Returns:
            User: The updated user.
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def change_password(self, email: str, new_password: str) -> User:
        """
        Change a user's password.

        Args:
            email (str): The email address of the user.
            new_password (str): The new password to set.

        Returns:
            User: The updated user.
        """
        user = await self.get_user_by_email(email)
        user.hashed_password = new_password
        await self.db.commit()
        await self.db.refresh(user)
        return user
