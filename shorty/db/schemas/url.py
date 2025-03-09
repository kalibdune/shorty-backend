from datetime import datetime, timedelta
from uuid import UUID

from pydantic import AnyUrl, BaseModel, Field, field_validator

from shorty.config import config


class UrlBaseSchema(BaseModel):
    url: AnyUrl
    hash: str = Field(max_length=config.app.hash_len)
    expired_at: datetime
    user_id: UUID


class UrlInDB(UrlBaseSchema):
    url: str


class UrlSchema(UrlBaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime


class UrlCreateSchema(BaseModel):
    url: AnyUrl
    user_id: UUID
    expiration_time: int = Field(ge=0, description="short url life duration in seconds")

    @field_validator("expiration_time")
    def parse_expiration_time(cls, value):
        if isinstance(value, int):
            return timedelta(seconds=value)
        return value


class UrlUpdateSchema(BaseModel):
    url: AnyUrl | None = None
    user_id: UUID | None = None
    hash: str | None = None
    expired_at: datetime | None = None
