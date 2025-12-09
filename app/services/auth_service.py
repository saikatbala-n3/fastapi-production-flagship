from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate


class AuthService:
    """Authentication service."""

    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
        """
        Authenticate user by username/email and password.

        Args:
            db: Database session
            username: Username or email
            password: Plain password

        Returns:
            User if authenticated, None otherwise
        """
        if "@" in username:
            result = await db.execute(select(User).where(User.email == username))
        else:
            result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
        """
        Create new user.

        Args:
            db: Database session
            user_in: User creation data

        Returns:
            Created user
        """
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email,
            username=user_in.username,
            full_name=user_in.full_name,
            hashed_password=hashed_password,
            is_active=user_in.is_active,
            role=user_in.role,
        )
        db.add(db_user)
        await db.flush()
        await db.refresh(db_user)

        return db_user

    @staticmethod
    def create_token(user_id: str) -> Token:
        """
        Create access and refresh tokens for user.

        Args:
            user_id: User ID

        Returns:
            Token pair
        """
        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)

        return Token(access_token=access_token, refresh_token=refresh_token)
