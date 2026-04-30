from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.users.models import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: str | None = None
    is_active: bool = True
    role: UserRole = UserRole.USER


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=50)
    full_name: str | None = None
    password: str | None = Field(None, min_length=8)


class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    full_name: str | None
    is_active: bool
    role: UserRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
