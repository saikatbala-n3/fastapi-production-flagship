from httpx import AsyncClient


async def _auth_headers(client, user_data):
    await client.post("/auth/register", json=user_data)
    login = await client.post(
        "/auth/login",
        json={
            "username": user_data["username"],
            "password": user_data["password"],
        },
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


async def test_get_me(client: AsyncClient, user_data):
    headers = await _auth_headers(client, user_data)
    r = await client.get("/users/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["email"] == user_data["email"]


async def test_update_me(client: AsyncClient, user_data):
    headers = await _auth_headers(client, user_data)
    r = await client.put("/users/me", json={"full_name": "Updated"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["full_name"] == "Updated"


async def test_unauthenticated(client: AsyncClient):
    r = await client.get("/users/me")
    assert r.status_code == 401


async def test_admin_list_requires_role(client: AsyncClient, user_data):
    headers = await _auth_headers(client, user_data)
    r = await client.get("/users/", headers=headers)
    assert r.status_code == 403


async def test_admin_can_list(client: AsyncClient):
    admin_data = {
        "email": "admin@example.com",
        "username": "adminuser",
        "password": "adminpass123",
        "role": "admin",
    }
    headers = await _auth_headers(client, admin_data)
    r = await client.get("/users/", headers=headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
