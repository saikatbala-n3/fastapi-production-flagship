from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core import cache
from app.core.database import get_session
from app.core.deps import get_current_user, require_role
from app.users.models import User, UserRole
from app.users.schemas import UserResponse, UserUpdate
from app.users.service import deactivate_user, get_user_by_id, get_users, update_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Update current user profile."""
    return await update_user(db, current_user.id, user_update, cache)


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    """Get user by id"""
    user = await get_user_by_id(db, str(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.get("/", response_model=list[UserResponse])
async def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_role(UserRole.ADMIN)),
):
    """Get list of users (admin only)."""
    return await get_users(db, skip, limit)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_role(UserRole.ADMIN)),
):
    """Delete user (admin only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    await deactivate_user(db, user)
