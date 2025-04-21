"""
SQLAlchemy models for database tables.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, func, Table
from sqlalchemy.orm import relationship, mapped_column, Mapped, DeclarativeBase
from sqlalchemy.sql.schema import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import DateTime


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class Contact(Base):
    """
    SQLAlchemy model for contacts table.

    Attributes:
        id (int): Primary key, auto-incrementing.
        user_id (int): Foreign key to users table, cascades on delete.
        first_name (str): First name of the contact, max 50 characters.
        last_name (str): Last name of the contact, max 50 characters.
        email (str): Email address of the contact, max 100 characters, unique.
        phone (str): Phone number of the contact, max 20 characters, unique.
        birthdate (datetime): Birth date of the contact, optional.
        additional_info (str): Additional information, max 255 characters, optional.
    """

    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None
    )
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    birthdate: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    additional_info: Mapped[str] = mapped_column(String(255), nullable=True)


class User(Base):
    """
    SQLAlchemy model for users table.

    Attributes:
        id (int): Primary key.
        username (str): Unique username.
        email (str): Unique email address.
        hashed_password (str): Hashed password string.
        created_at (datetime): Timestamp of user creation.
        avatar (str): URL to user's avatar image, max 255 characters, optional.
        confirmed (bool): Email confirmation status, defaults to False.
    """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
