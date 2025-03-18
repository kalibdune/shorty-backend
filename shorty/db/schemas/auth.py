from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TokensSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class AccessTokenChangeSchema(BaseModel):
    refresh_token: str


class RefreshTokenBase(BaseModel):
    expired_at: datetime
    refresh_token: str
    user_id: UUID


class RefreshTokenSchema(RefreshTokenBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class RefreshTokenCreateSchema(RefreshTokenBase):
    expired_at: datetime
    refresh_token: str
    user_id: UUID
