"""
User service module for managing user-related business logic.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.schemas import UserCreate
from src.database.models import User


class UserService:
    """
    Service class for handling user-related business logic.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the service with a database session.

        Args:
            db (AsyncSession): The database session to use.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Create a new user with an automatically generated Gravatar avatar.

        Args:
            body (UserCreate): The user data for creating a new user.

        Returns:
            User: The created user object.
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
        Retrieve a user by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            User | None: The user if found, otherwise None.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Retrieve a user by their username.

        Args:
            username (str): The username of the user to retrieve.

        Returns:
            User | None: The user if found, otherwise None.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Retrieve a user by their email address.

        Args:
            email (str): The email address of the user to retrieve.

        Returns:
            User | None: The user if found, otherwise None.
        """
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str):
        """
        Mark a user's email as confirmed.

        Args:
            email (str): The email address of the user to confirm.

        Returns:
            None
        """
        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str):
        """
        Update a user's avatar URL.

        Args:
            email (str): The email address of the user.
            url (str): The new avatar URL.

        Returns:
            User: The updated user object.
        """
        return await self.repository.update_avatar_url(email, url)

    async def change_password(self, email: str, new_password: str) -> User:
        """
        Change a user's password.

        Args:
            email (str): The email address of the user.
            new_password (str): The new password to set.

        Returns:
            User: The updated user object.
        """
        return await self.repository.change_password(email, new_password)
