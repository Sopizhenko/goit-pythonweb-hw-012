import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from src.schemas import ContactCreate, ContactUpdate, ContactUpdateBirthdate


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)


@pytest.fixture
def test_user():
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password123",
    )


@pytest.fixture
def test_contact():
    return Contact(
        id=1,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="1234567890",
        birthdate=date(1990, 1, 1),
        user_id=1
    )


async def test_get_contacts(mock_session, contact_repository, test_user, test_contact):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_result
    mock_result.all.return_value = [test_contact]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.get_contacts(
        user=test_user,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com"
    )

    # Assertions
    assert len(result) == 1
    assert result[0].id == test_contact.id
    assert result[0].first_name == test_contact.first_name
    mock_session.execute.assert_called_once()


async def test_get_contact_by_id(mock_session, contact_repository, test_user, test_contact):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.get_contact_by_id(1, test_user)

    # Assertions
    assert result == test_contact
    mock_session.execute.assert_called_once()


async def test_get_contact_by_id_not_found(mock_session, contact_repository, test_user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.get_contact_by_id(999, test_user)

    # Assertions
    assert result is None
    mock_session.execute.assert_called_once()


async def test_create_contact(mock_session, contact_repository, test_user, test_contact):
    # Setup mock
    contact_data = ContactCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="1234567890",
        birthdate=date(1990, 1, 1)
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_contact
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    # Call method
    result = await contact_repository.create_contact(contact_data, test_user)

    # Assertions
    assert isinstance(result, Contact)
    assert result.first_name == contact_data.first_name
    assert result.last_name == contact_data.last_name
    assert result.email == contact_data.email
    assert result.user_id == test_user.id


async def test_update_contact(mock_session, contact_repository, test_user, test_contact):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_contact
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    
    update_data = ContactUpdate(
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com"
    )

    # Call method
    result = await contact_repository.update_contact(1, update_data, test_user)

    # Assertions
    assert result.first_name == "Jane"
    assert result.last_name == "Smith"
    assert result.email == "jane.smith@example.com"
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


async def test_update_contact_not_found(mock_session, contact_repository, test_user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    update_data = ContactUpdate(first_name="Jane")

    # Call method
    result = await contact_repository.update_contact(999, update_data, test_user)

    # Assertions
    assert result is None
    mock_session.commit.assert_not_called()


async def test_update_contact_birthdate(mock_session, contact_repository, test_user, test_contact):
    # Setup mock
    mock_result = MagicMock()
    test_contact_copy = Contact(
        id=1,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="1234567890",
        birthdate=datetime(1990, 1, 1),
        user_id=1
    )
    mock_result.scalar_one_or_none.return_value = test_contact_copy
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    
    new_birthdate = datetime(1991, 2, 2)
    birthdate_update = ContactUpdateBirthdate(birthdate=new_birthdate)

    # Call method
    result = await contact_repository.update_contact_birthdate(1, birthdate_update, test_user)

    # Assertions
    assert isinstance(result.birthdate, datetime)
    assert result.birthdate == new_birthdate
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


async def test_get_birthdays_next_week(mock_session, contact_repository, test_user, test_contact):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_result
    mock_result.all.return_value = [test_contact]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.get_birthdays_next_week(test_user)

    # Assertions
    assert len(result) == 1
    assert result[0] == test_contact
    mock_session.execute.assert_called_once()


async def test_delete_contact(mock_session, contact_repository, test_user, test_contact):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_contact
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.delete = AsyncMock()
    mock_session.commit = AsyncMock()

    # Call method
    result = await contact_repository.delete_contact(1, test_user)

    # Assertions
    assert result == test_contact
    mock_session.delete.assert_called_once_with(test_contact)
    mock_session.commit.assert_called_once()


async def test_delete_contact_not_found(mock_session, contact_repository, test_user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.delete_contact(999, test_user)

    # Assertions
    assert result is None
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()
