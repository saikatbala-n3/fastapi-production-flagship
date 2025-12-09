import json
from typing import Any, Optional

from redis.asyncio import Redis

from app.core.config import settings


class CacheManager:
    """Redis cache manager."""

    def __init__(self):
        self.redis: Optional[Redis] = None

    async def connect(self):
        """Connect to Redis."""
        self.redis = await Redis.from_url(
            str(settings.REDIS_URL), encoding="utf-8", decode_response=True
        )

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if not self.redis:
            return None

        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Any, expire: int = 300) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            expire: Expiration time in seconds (default 5 minutes)

        Returns:
            True if successful
        """
        if not self.redis:
            return False

        return await self.redis.setex(key, expire, json.dumps(value))

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted
        """
        if not self.redis:
            return False

        return await self.redis.delete(key) > 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.redis:
            return False

        return await self.redis.exists(key) > 0


cache = CacheManager()


async def get_cache():
    """Dependancy to get cache instance."""
    return cache
