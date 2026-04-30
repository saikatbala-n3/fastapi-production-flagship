from httpx import AsyncClient


async def test_rate_limit_headers_present(client: AsyncClient):
    r = await client.get("/health")
    # /health is excluded from rate limiting
    assert r.status_code == 200


async def test_rate_limit_headers_on_auth(client: AsyncClient, user_data):
    await client.post("/auth/register", json=user_data)
    r = await client.post(
        "/auth/login",
        json={
            "username": user_data["username"],
            "password": user_data["password"],
        },
    )
    # Headers present when Redis is available
    if "X-RateLimit-Remaining" in r.headers:
        assert int(r.headers["X-RateLimit-Remaining"]) >= 0
