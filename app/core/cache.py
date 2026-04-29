import json

from redis.asyncio import Redis

from app.core.config import settings

_redis: Redis | None = None


async def connect(self):
    global _redis
    _redis = Redis.from_url(settings.redis_url, decode_responses=True)


async def disconnect(self):
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


async def client():
    return _redis


async def get(key: str):
    if not _redis:
        return None

    value = await _redis.get(key)
    return json.loads(value) if value else None


async def set(key: str, value: Any, expire: int = 300) -> bool:
    if not _redis:
        return False
    return await _redis.setex(key, expire, json.dumps(value, default=str))


async def delete(key: str) -> bool:
    if not _redis:
        return False

    return await _redis.delete(key) > 0
