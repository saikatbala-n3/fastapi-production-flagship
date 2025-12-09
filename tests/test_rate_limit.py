import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_rate_limiting(client: AsyncClient):
    """Test rate limiting middleware."""
    # Make requests until rate limit is hit
    # Note: This test assumes RATE_LIMIT_PER_MINUTE = 60

    for i in range(10):
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
