"""
Database connection management module.
Provides async session management and dependency injection for FastAPI.
"""

import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.conf.config import settings


class DatabaseSessionManager:
    """
    Manages database sessions for the application.
    Provides async context management for database sessions.
    """

    def __init__(self, url: str):
        """
        Initialize the session manager.

        Args:
            url (str): Database connection URL.
        """
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Create a context-managed database session.

        Yields:
            AsyncSession: An async SQLAlchemy session.

        Raises:
            Exception: If the session is not initialized.
            SQLAlchemyError: If a database error occurs.
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise  # Re-raise the original error
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(settings.DB_URL)


async def get_db():
    """
    FastAPI dependency for database session injection.
    
    Yields:
        AsyncSession: An async SQLAlchemy session.
    """
    async with sessionmanager.session() as session:
        yield session
