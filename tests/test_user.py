import pytest
from httpx import AsyncClient


async def get_auth_headers(client: AsyncClient, test_user_data) -> dict:
    """Helper function to get authentication headers."""
    await client.post("/api/v1/auth/register", json=test_user_data)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        },
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, test_user_data):
    """Test getting current user profile."""
    headers = await get_auth_headers(client, test_user_data)

    response = await client.get("/api/v1/users/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["username"] == test_user_data["username"]


@pytest.mark.asyncio
async def test_update_current_user(client: AsyncClient, test_user_data):
    """Test updating current user profile."""
    headers = await get_auth_headers(client, test_user_data)

    update_data = {"full_name": "Updated Name"}
    response = await client.put("/api/v1/users/me", json=update_data, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"


@pytest.mark.asyncio
async def test_get_user_without_auth(client: AsyncClient):
    """Test accessing user endpoint without authentication."""
    response = await client.get("/api/v1/users/me")

    assert response.status_code == 401
