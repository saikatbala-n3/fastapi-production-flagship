import time

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.cache import cache
from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis token bucket algorithm.

    Limits requests per IP address.
    """

    async def dispatch(self, request: Request, call_next):
        # Skip rate limit for health check
        if request.url.path == "/health":
            return await call_next(request)

        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"

        # Token bucket parameters
        capacity = settings.RATE_LIMIT_PER_MINUTE
        refill_rate = capacity / 60.0

        # Skip rate limiting if Redis is not available
        if not cache.redis:
            return await call_next(request)

        # Get current bucket state
        bucket_data = await cache.get(key)
        current_time = time.time()

        # Initialize bucket
        if bucket_data is None:
            tokens = capacity - 1
            last_refill = current_time
        else:
            tokens = bucket_data["tokens"]
            last_refill = bucket_data["last_refill"]

            time_passed = current_time - last_refill
            tokens = min(capacity, int(tokens + time_passed * refill_rate))

            if tokens < 1:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Try again later.",
                )
            tokens -= 1

        await cache.set(key, {"tokens": tokens, "last_refill": current_time}, expire=60)

        response = await call_next(request)

        # Add rate limiting headers
        response.headers["X-RateLimit-Limit"] = str(capacity)
        response.headers["X-RateLimit-Remaining"] = str(int(tokens))

        return response
