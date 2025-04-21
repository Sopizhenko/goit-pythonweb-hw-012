import io
from unittest.mock import Mock, patch, AsyncMock

import pytest
from sqlalchemy import select

from src.database.models import User, UserRole
from tests.conftest import TestingSessionLocal, test_admin_user, test_user


@pytest.mark.asyncio
async def test_get_me(client, get_token):
    response = client.get(
        "/api/users/me", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]


@pytest.mark.asyncio
async def test_get_me_rate_limit(client, get_token):
    # Test rate limiting (10 requests per minute)
    for _ in range(11):
        response = client.get(
            "/api/users/me", headers={"Authorization": f"Bearer {get_token}"}
        )
    assert response.status_code == 429


@pytest.mark.asyncio
async def test_update_avatar(client, get_token):
    # Create a mock user with the expected avatar URL
    mock_user = User(
        id=1,
        username="user",
        email="user@example.com",
        avatar="https://fake-avatar-url.com/avatar.png",
        role=UserRole.USER,
        confirmed=True,
    )

    with patch(
        "src.api.users.UserService.update_avatar_url", new_callable=AsyncMock
    ) as mock_update_avatar:
        mock_update_avatar.return_value = (
            mock_user  # Use our mock user instead of test_admin_user
        )
        with patch(
            "src.api.users.UploadFileService.upload_file", new_callable=Mock
        ) as mock_upload:
            mock_upload.return_value = "https://fake-avatar-url.com/avatar.png"

            fake_file = io.BytesIO(b"avatar image data")
            fake_file.name = "avatar.png"

            response = client.patch(
                "/api/users/avatar",
                headers={"Authorization": f"Bearer {get_token}"},
                files={"file": ("avatar.png", fake_file, "image/png")},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["avatar"] == "https://fake-avatar-url.com/avatar.png"


@pytest.mark.asyncio
async def test_update_avatar_no_file(client, get_token):
    response = client.patch(
        "/api/users/avatar",
        headers={"Authorization": f"Bearer {get_token}"},
        files={},  # Send empty files dict to trigger validation error
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data  # Verify that we get a validation error detail


@pytest.mark.asyncio
async def test_update_avatar_unauthorized(client):
    fake_file = io.BytesIO(b"avatar image data")
    response = client.patch(
        "/api/users/avatar",
        files={"file": ("avatar.png", fake_file, "image/png")},
    )
    assert response.status_code == 401
