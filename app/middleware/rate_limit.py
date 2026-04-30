import time

from fastapi import Request, status
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.cache import cache
from app.core.config import settings
from app.metrics import rate_limit_decisions

EXCLUDED = {"/health", "/metrics", "/openapi.json"}


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXCLUDED:
            return await call_next(request)

        if not cache.client():
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}"
        capacity = settings.rate_limit_per_minute
        refill_rate = capacity / 60.0

        bucket_data = await cache.get(key)
        current_time = time.time()
        if bucket_data is None:
            tokens = capacity - 1
        else:
            time_passed = current_time - bucket_data["last_refill"]
            tokens = min(capacity, int(tokens + time_passed * refill_rate))

        if tokens < 0:
            rate_limit_decisions.labels(decisions="deny").inc()
            raise JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded"},
                headers={"X-RateLimit-Remaining": "0"},
            )

        rate_limit_decisions.labels(decision="allow").inc()
        await cache.set(key, {"tokens": tokens, "last_refill": current_time}, expire=60)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(capacity)
        response.headers["X-RateLimit-Remaining"] = str(int(tokens))
        return response
