from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    is_active: bool = True
    role: UserRole.USER


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """User update schema."""

    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """User schema with database fields."""

    model_config = ConfigDict(from_attributes=True)
    id: str
    hashed_password: str


class UserResponse(UserBase):
    """User response schema (public)."""

    model_config = ConfigDict(from_attributes=True)
    id: str


class LoginRequest(BaseModel):
    """Login request schema."""

    username: str  # Can be username or email
    password: str
