from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    # bcrypt обрабатывает только первые 72 байта пароля (в UTF-8 это может быть
    # меньше 72 символов). Валидируем, чтобы не было сюрпризов и 500 ошибок.
    password: str = Field(min_length=8, max_length=256)

    @field_validator("password")
    @classmethod
    def password_max_72_bytes(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes (bcrypt limit)")
        return v


class UserOut(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)