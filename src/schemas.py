"""
Pydantic models for data validation and serialization.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class ContactBase(BaseModel):
    """
    Base model for contact information.

    Attributes:
        first_name (str): First name of the contact, max length 50 characters.
        last_name (str): Last name of the contact, max length 50 characters.
        email (str): Email address of the contact, max length 100 characters.
        phone (str): Phone number of the contact, max length 20 characters.
        birthdate (Optional[datetime]): Birth date of the contact.
        additional_info (Optional[str]): Additional information about the contact, max length 255 characters.
    """

    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: str = Field(max_length=100)
    phone: str = Field(max_length=20)
    birthdate: Optional[datetime] = None
    additional_info: Optional[str] = Field(None, max_length=255)

    model_config = ConfigDict(from_attributes=True)


class ContactCreate(ContactBase):
    """
    Model for creating a new contact. Inherits all fields from ContactBase.
    """

    pass


class ContactUpdate(ContactBase):
    """
    Model for updating an existing contact.
    All fields are optional to allow partial updates.
    """

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    birthdate: Optional[datetime] = None
    additional_info: Optional[str] = None


class ContactUpdateBirthdate(BaseModel):
    """
    Model for updating only the birthdate of a contact.

    Attributes:
        birthdate (datetime): The new birthdate to set.
    """

    birthdate: datetime


class ContactModel(ContactBase):
    """
    Model for contact responses, includes all base fields plus the contact ID.

    Attributes:
        id (int): Unique identifier for the contact.
    """

    id: int

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    """
    Model for user responses.

    Attributes:
        id (int): Unique identifier for the user.
        username (str): Username of the user.
        email (str): Email address of the user.
        avatar (str): URL of the user's avatar image.
    """

    id: int
    username: str
    email: str
    avatar: str

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    Model for creating a new user.

    Attributes:
        username (str): Desired username for the new user.
        email (str): Email address for the new user.
        password (str): Password for the new user.
    """

    username: str
    email: str
    password: str


class Token(BaseModel):
    """
    Model for authentication tokens.

    Attributes:
        access_token (str): The JWT access token.
        token_type (str): The type of token (e.g., "bearer").
    """

    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    """
    Model for requesting email verification.

    Attributes:
        email (EmailStr): The email address to verify.
    """

    email: EmailStr
