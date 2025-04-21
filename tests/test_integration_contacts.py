from datetime import datetime, timedelta
import pytest
from unittest.mock import AsyncMock, patch

from src.database.models import Contact, User
from src.schemas import ContactCreate, ContactUpdate, ContactUpdateBirthdate
from tests.conftest import TestingSessionLocal


@pytest.fixture
def test_contact_data():
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "1234567890",
        "birthdate": "1990-01-01T00:00:00",
        "additional_info": "Test contact",
    }


@pytest.mark.asyncio
async def test_create_contact(client, get_token, test_contact_data):
    response = client.post(
        "/api/contacts/",
        json=test_contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == test_contact_data["first_name"]
    assert data["last_name"] == test_contact_data["last_name"]
    assert data["email"] == test_contact_data["email"]
    assert data["phone"] == test_contact_data["phone"]
    assert "id" in data


@pytest.mark.asyncio
async def test_get_contacts(client, get_token, test_contact_data):
    # Create a contact with a different phone number
    contact_data = test_contact_data.copy()
    contact_data["phone"] = "9876543210"
    contact_data["email"] = "john2.doe@example.com"

    response = client.post(
        "/api/contacts/",
        json=contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )

    # Then get all contacts
    response = client.get(
        "/api/contacts/",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Check if any contact in the list matches our test data
    assert any(contact["phone"] == contact_data["phone"] for contact in data)


@pytest.mark.asyncio
async def test_get_contact_by_id(client, get_token, test_contact_data):
    # Create a contact with a different phone number
    contact_data = test_contact_data.copy()
    contact_data["phone"] = "5555555555"
    contact_data["email"] = "john3.doe@example.com"

    create_response = client.post(
        "/api/contacts/",
        json=contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    created_contact = create_response.json()

    # Then get it by id
    response = client.get(
        f"/api/contacts/{created_contact['id']}",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_contact["id"]
    assert data["first_name"] == contact_data["first_name"]


@pytest.mark.asyncio
async def test_get_contact_not_found(client, get_token):
    response = client.get(
        "/api/contacts/999999", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Contact not found"


@pytest.mark.asyncio
async def test_update_contact(client, get_token, test_contact_data):
    # Create a contact with a different phone number
    contact_data = test_contact_data.copy()
    contact_data["phone"] = "1111111111"
    contact_data["email"] = "john4.doe@example.com"

    create_response = client.post(
        "/api/contacts/",
        json=contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    created_contact = create_response.json()

    # Update the contact
    update_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "phone": "2222222222",
        "additional_info": "Updated contact",
    }

    response = client.put(
        f"/api/contacts/{created_contact['id']}",
        json=update_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == update_data["first_name"]
    assert data["last_name"] == update_data["last_name"]
    assert data["email"] == update_data["email"]


@pytest.mark.asyncio
async def test_update_contact_birthdate(client, get_token, test_contact_data):
    # Create a contact with a different phone number
    contact_data = test_contact_data.copy()
    contact_data["phone"] = "3333333333"
    contact_data["email"] = "john5.doe@example.com"

    create_response = client.post(
        "/api/contacts/",
        json=contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    created_contact = create_response.json()

    # Update birthdate
    new_birthdate = {"birthdate": "1995-06-15T00:00:00"}

    response = client.patch(
        f"/api/contacts/{created_contact['id']}/birthdate",
        json=new_birthdate,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "1995-06-15" in data["birthdate"]


@pytest.mark.asyncio
async def test_delete_contact(client, get_token, test_contact_data):
    # Create a contact with a different phone number
    contact_data = test_contact_data.copy()
    contact_data["phone"] = "4444444444"
    contact_data["email"] = "john6.doe@example.com"

    create_response = client.post(
        "/api/contacts/",
        json=contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    created_contact = create_response.json()

    # Delete the contact
    response = client.delete(
        f"/api/contacts/{created_contact['id']}",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200

    # Verify it's deleted
    get_response = client.get(
        f"/api/contacts/{created_contact['id']}",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_unauthorized_access(client, test_contact_data):
    # Try to access endpoints without authentication
    endpoints = [
        ("GET", "/api/contacts/"),
        ("POST", "/api/contacts/"),
        ("GET", "/api/contacts/1"),
        ("PUT", "/api/contacts/1"),
        ("PATCH", "/api/contacts/1/birthdate"),
        ("DELETE", "/api/contacts/1"),
        ("GET", "/api/contacts/birthdays_next_week"),
    ]

    for method, endpoint in endpoints:
        if method == "GET":
            response = client.get(endpoint)
        elif method == "POST":
            response = client.post(endpoint, json=test_contact_data)
        elif method == "PUT":
            response = client.put(endpoint, json=test_contact_data)
        elif method == "PATCH":
            response = client.patch(endpoint, json={"birthdate": "1990-01-01T00:00:00"})
        elif method == "DELETE":
            response = client.delete(endpoint)

        assert response.status_code == 401, f"Expected 401 for {method} {endpoint}"


@pytest.mark.asyncio
async def test_contact_search(client, get_token, test_contact_data):
    # Create a contact with a different phone number
    contact_data = test_contact_data.copy()
    contact_data["phone"] = "7777777777"
    contact_data["email"] = "john7.doe@example.com"

    client.post(
        "/api/contacts/",
        json=contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )

    # Test different search parameters
    search_params = [
        {"first_name": contact_data["first_name"]},
        {"last_name": contact_data["last_name"]},
        {"email": contact_data["email"]},
    ]

    for params in search_params:
        response = client.get(
            "/api/contacts/",
            params=params,
            headers={"Authorization": f"Bearer {get_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert any(
            contact[list(params.keys())[0]] == list(params.values())[0]
            for contact in data
        )
