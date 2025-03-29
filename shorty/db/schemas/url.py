from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID

from pydantic import AnyUrl, BaseModel, Field, field_validator

from shorty.config import config


class UrlBaseSchema(BaseModel):
    url: AnyUrl
    hash: str = Field(max_length=config.app.hash_len)
    expired_at: datetime | None
    user_id: UUID | None


class UrlInDB(UrlBaseSchema):
    url: str


class UrlSchema(UrlBaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime


class UrlCreateSchema(BaseModel):
    url: AnyUrl
    expiration_time: (
        Annotated[
            datetime,
            Field(
                ge=datetime.now(),
                description="short url life duration in datetime greater or equals current time",
            ),
        ]
        | None
    )

    @field_validator("expiration_time")
    def parse_expiration_time(cls, value):
        if value:
            return value.replace(tzinfo=None)
        return value


class UrlUpdateSchema(BaseModel):
    url: AnyUrl | None = None
    user_id: UUID | None = None
    hash: str | None = None
    expired_at: datetime | None = None
