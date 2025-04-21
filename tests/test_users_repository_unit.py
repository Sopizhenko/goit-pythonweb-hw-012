import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserCreate
from src.repository.users import UserRepository


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def user_repository(mock_session):
    return UserRepository(mock_session)


@pytest.fixture
def test_user():
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password123",
        confirmed=False,
        avatar=None,
    )


async def test_get_user_by_id(user_repository, test_user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    user_repository.db.execute.return_value = mock_result

    # Call method
    result = await user_repository.get_user_by_id(1)

    # Assertions
    assert result == test_user
    user_repository.db.execute.assert_called_once()


async def test_get_user_by_id_not_found(user_repository):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    user_repository.db.execute.return_value = mock_result

    # Call method
    result = await user_repository.get_user_by_id(1)

    # Assertions
    assert result is None
    user_repository.db.execute.assert_called_once()


async def test_get_user_by_username(user_repository, test_user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    user_repository.db.execute.return_value = mock_result

    # Call method
    result = await user_repository.get_user_by_username("testuser")

    # Assertions
    assert result == test_user
    user_repository.db.execute.assert_called_once()


async def test_get_user_by_email(user_repository, test_user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    user_repository.db.execute.return_value = mock_result

    # Call method
    result = await user_repository.get_user_by_email("test@example.com")

    # Assertions
    assert result == test_user
    user_repository.db.execute.assert_called_once()


async def test_create_user(user_repository, test_user):
    # Setup mock
    user_data = UserCreate(
        username="testuser", email="test@example.com", password="hashed_password123"
    )
    user_repository.db.commit.return_value = None
    user_repository.db.refresh.return_value = None

    # Call method
    result = await user_repository.create_user(user_data)

    # Assertions
    assert isinstance(result, User)
    assert result.username == user_data.username
    assert result.email == user_data.email
    user_repository.db.add.assert_called_once()
    user_repository.db.commit.assert_called_once()
    user_repository.db.refresh.assert_called_once()


async def test_confirmed_email(user_repository, test_user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    user_repository.db.execute.return_value = mock_result

    # Call method
    await user_repository.confirmed_email("test@example.com")

    # Assertions
    assert test_user.confirmed is True
    user_repository.db.commit.assert_called_once()


async def test_update_avatar_url(user_repository, test_user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    user_repository.db.execute.return_value = mock_result
    new_avatar_url = "http://example.com/avatar.jpg"

    # Call method
    result = await user_repository.update_avatar_url("test@example.com", new_avatar_url)

    # Assertions
    assert result.avatar == new_avatar_url
    user_repository.db.commit.assert_called_once()
    user_repository.db.refresh.assert_called_once()
