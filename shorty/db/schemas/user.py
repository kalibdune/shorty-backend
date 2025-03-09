from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserBaseSchema(BaseModel):
    name: str
    email: EmailStr


class UserSchema(UserBaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime


class UserCreateSchema(UserBaseSchema):
    password: str


class UserUpdateSchema(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
