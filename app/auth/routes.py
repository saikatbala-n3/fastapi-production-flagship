from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status

from app.core import cache
from app.users.models import User
from app.core.deps import oauth2_scheme
from app.core.database import get_session
from app.auth.security import decode_token
from app.auth.schemas import Token, LoginRequest
from app.users.schemas import UserCreate, UserResponse
from app.auth.service import authenticate_user, create_user, issue_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_session)):
    try:
        user = await create_user(db, user_in)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or Username already registered",
        )
    return user


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_session)):
    """Authenticate and return tokens."""
    user = await authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return issue_token(user.id)


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_session)):
    """Refresh access token using refresh token."""
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    result = await db.execute(select(User).where(User.id == payload["sub"]))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return issue_token(user.id)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(token: str = Depends(oauth2_scheme)):
    """Revoke the current access token by adding it to the Redis blocklist."""
    payload = decode_token(token)
    if payload:
        remaining = int(payload.get("exp", 0)) - datetime.now(timezone.utc).timestamp()
        if remaining > 0:
            await cache.set(f"blocked:{token}", "1", expire=remaining)
