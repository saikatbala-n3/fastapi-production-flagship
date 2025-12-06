from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.cache import get_cache, CacheManager
from app.api.deps import get_current_user, get_current_superuser
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService
from app.models.user import User

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    cache: CacheManager = Depends(get_cache),
):
    """Update current user profile."""
    updated_user = await UserService.user_update(
        db, current_user.id, user_update, cache
    )
    return updated_user


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    cache: CacheManager = Depends(get_cache),
    current_user: User = Depends(get_current_user),
):
    """Get user by id"""
    user = await UserService.get_user_by_id(db, user_id, cache)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.get("/", response_model=List(UserResponse))
async def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get list of users (admin only).

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
    """
    users = await UserService.get_users(db, skip, limit)
    return users


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    cache: CacheManager = Depends(get_cache),
    current_user: User = Depends(get_current_superuser),
):
    """Delete user (admin only)."""
    deleted = await UserService.delete_user(db, user_id, cache)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
