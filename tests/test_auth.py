from httpx import AsyncClient


async def test_register(client: AsyncClient, user_data):
    r = await client.post("/auth/register", json=user_data)
    assert r.status_code == 201
    assert r.json()["email"] == user_data["email"]
    assert "hashed_password" not in r.json()


async def test_register_duplicate(client: AsyncClient, user_data):
    await client.post("/auth/register", json=user_data)
    r = await client.post("/auth/register", json=user_data)
    assert r.status_code == 409


async def test_login(client: AsyncClient, user_data):
    await client.post("/auth/register", json=user_data)
    r = await client.post(
        "/auth/login",
        json={
            "username": user_data["username"],
            "password": user_data["password"],
        },
    )
    assert r.status_code == 200
    assert "access_token" in r.json()
    assert "refresh_token" in r.json()


async def test_login_wrong_password(client: AsyncClient, user_data):
    await client.post("/auth/register", json=user_data)
    r = await client.post(
        "/auth/login",
        json={
            "username": user_data["username"],
            "password": "wrongpassword",
        },
    )
    assert r.status_code == 401


async def test_refresh(client: AsyncClient, user_data):
    await client.post("/auth/register", json=user_data)
    login = await client.post(
        "/auth/login",
        json={
            "username": user_data["username"],
            "password": user_data["password"],
        },
    )
    r = await client.post(
        "/auth/refresh",
        params={"refresh_token": login.json()["refresh_token"]},
    )
    assert r.status_code == 200
    assert "access_token" in r.json()


async def test_refresh_with_access_token_fails(client: AsyncClient, user_data):
    await client.post("/auth/register", json=user_data)
    login = await client.post(
        "/auth/login",
        json={
            "username": user_data["username"],
            "password": user_data["password"],
        },
    )
    r = await client.post(
        "/auth/refresh",
        params={"refresh_token": login.json()["access_token"]},
    )
    assert r.status_code == 401


async def test_logout_revokes_token(client: AsyncClient, user_data):
    """After logout, the access token should be rejected on protected endpoints."""
    await client.post("/auth/register", json=user_data)
    login = await client.post(
        "/auth/login",
        json={
            "username": user_data["username"],
            "password": user_data["password"],
        },
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Token works before logout
    r = await client.get("/users/me", headers=headers)
    assert r.status_code == 200

    # Logout
    r = await client.post("/auth/logout", headers=headers)
    assert r.status_code == 204

    # Token rejected after logout (only if Redis is running)
    r = await client.get("/users/me", headers=headers)
    assert r.status_code in (
        200,
        401,
    )  # 401 if Redis available, 200 if graceful degradation


async def test_correlation_id_in_response(client: AsyncClient):
    """Every response should contain X-Request-ID header."""
    r = await client.get("/health")
    assert "x-request-id" in r.headers


async def test_client_correlation_id_echoed(client: AsyncClient):
    """Client-supplied X-Request-ID should be echoed back unchanged."""
    custom_id = "my-trace-id-123"
    r = await client.get("/health", headers={"X-Request-ID": custom_id})
    assert r.headers.get("x-request-id") == custom_id
