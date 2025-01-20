from datetime import datetime, timedelta
from uuid import UUID

from pydantic import AnyUrl, BaseModel, Field, field_validator


class UrlBaseSchema(BaseModel):
    url: AnyUrl
    hash: str = Field(max_length=5)
    expired_at: datetime


class UrlInDB(UrlBaseSchema): ...


class UrlSchema(UrlBaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime


class UrlCreateSchema(BaseModel):
    url: AnyUrl
    expiration_time: int = Field(description="short url life duration in seconds")

    @field_validator("expiration_time")
    def parse_expiration_time(cls, value):
        if isinstance(value, int):
            return timedelta(seconds=value)
        return value


class UrlUpdateSchema(BaseModel):
    url: AnyUrl | None = None
    hash: str | None = None
    expired_at: datetime | None = None
