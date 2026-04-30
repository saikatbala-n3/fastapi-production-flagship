from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.users.models import User
from app.auth.schemas import Token
from app.users.schemas import UserCreate


async def authenticate_user(
    session: AsyncSession, username: str, password: str
) -> User | None:
    field = User.email if "@" in username else User.username
    result = await session.execute(select(User).where(field == username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


async def create_user(session: AsyncSession, user_in: UserCreate) -> User:
    user = User(
        email=user_in.email,
        username=user_in.username,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    await session.commit()
    return user


def issue_token(user_id: str) -> Token:
    access_token = create_access_token(str(user_id))
    refresh_token = create_refresh_token(str(user_id))

    return Token(access_token=access_token, refresh_token=refresh_token)
