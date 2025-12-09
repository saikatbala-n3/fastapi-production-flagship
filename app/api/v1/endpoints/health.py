from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CacheManager, get_cache
from app.core.database import get_db

router = APIRouter()


@router.get("/health")
async def health_check(
    db: AsyncSession = Depends(get_db), cache: CacheManager = Depends(get_cache)
):
    """
    Health check endpoint.

    Returns service health status.
    """
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # Check redis
    try:
        if cache.redis:
            await cache.redis.ping()
            cache_status = "healthy"
        else:
            cache_status = "not connected"
    except Exception as e:
        cache_status = f"unhealthy: {str(e)}"

    return {"status": "ok", "database": db_status, "cache": cache_status}
