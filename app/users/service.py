from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import cache
from app.users.models import User
from app.users.schemas import UserUpdate
from app.auth.security import get_password_hash
from app.metrics import cache_hits, cache_misses


async def get_user_by_id(db: AsyncSession, user_id: str):
    """Fetch user by ID — check cache first, fall back to DB."""
    cache_key = f"user:{user_id}"
    cached_user = await cache.get(cache_key)
    if cached_user:
        cache_hits.labels(operation="get_user").inc()
        return User(**cached_user)

    cache_misses.labels(operation="get_user").inc()
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user:
        user_dict = {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "role": user.role.value,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at_at.isoformat(),
        }
        await cache.set(cache_key, user_dict)
    return user


async def deactivate_user(db: AsyncSession, user: User):
    """Delete user (soft delete by deactivating)."""
    user.is_active = False
    await db.flush()
    await db.commit()
    await cache.delete(f"user:{user.id}")


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())


async def update_user(db: AsyncSession, user: User, user_update: UserUpdate):
    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.flush()
    await db.refresh(user)
    await db.commit()
    await cache.delete(f"user:{user.id}")

    return user
