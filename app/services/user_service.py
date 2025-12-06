from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.schemas.user import UserUpdate
from app.core.security import get_password_hash
from app.core.cache import CacheManager


class UserService:
    """User service with caching."""

    @staticmethod
    async def get_user_by_id(
        db: AsyncSession, user_id: str, cache: Optional[CacheManager] = None
    ) -> Optional[User]:
        """
        Get user by ID with caching.

        Args:
            db: Database session
            user_id: User ID
            cache: Cache manager

        Returns:
            User or None
        """
        # Try cache first
        if cache:
            cache_key = f"user:{user_id}"
            cached_user = await cache.get(cache_key)
            if cached_user:
                return User(**cached_user)

        # Fetch from database
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        # Cache result
        if user and cache:
            user_dict = {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "role": user.role.value,
            }
            await cache.set(cache_key, user_dict, expire=300)

        return user

    @staticmethod
    async def delete_user(
        db: AsyncSession, user_id: str, cache: Optional[CacheManager] = None
    ) -> bool:
        """
        Delete user (soft delete by deactivating).

        Args:
            db: Database session
            user_id: User ID
            cache: Cache manager

        Returns:
            True if deleted
        """
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            return False

        user.is_active = False
        await db.flush()

        # Invalidate cache
        if cache:
            await cache.delete(f"user:{user_id}")

        return True

    @staticmethod
    async def get_users(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """
        Get list of users with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of users
        """
        result = await db.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())

    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: str,
        user_update: UserUpdate,
        cache: Optional[CacheManager] = None,
    ) -> Optional[User]:
        """
        Update user.

        Args:
            db: Database session
            user_id: User ID
            user_update: Update data
            cache: Cache manager

        Returns:
            Updated user or None
        """
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            return None

        # Update fields
        update_data = user_update.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(
                update_data.pop("password")
            )

        for field, value in update_data.items():
            setattr(user, field, value)

        await db.flush()
        await db.refresh(user)

        # Invalidate cache
        if cache:
            await cache.delete(f"user:{user_id}")

        return user
