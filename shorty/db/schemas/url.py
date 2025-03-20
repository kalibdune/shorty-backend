from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID

from pydantic import AnyUrl, BaseModel, Field, field_validator, model_validator

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
    user_id: UUID | None
    expiration_time: (
        Annotated[int, Field(ge=0, description="short url life duration in seconds")]
        | None
    )

    @field_validator("expiration_time")
    def parse_expiration_time(cls, value):
        if isinstance(value, int) and value != 0:
            return timedelta(seconds=value)
        return value

    @model_validator(mode="after")
    def check_user_id_and_expiration_time(cls, values):
        if values.user_id is None and values.expiration_time == 0:
            raise ValueError(
                "user_id=None and expiration_time=0 could not be at the same time"
            )
        return values


class UrlUpdateSchema(BaseModel):
    url: AnyUrl | None = None
    user_id: UUID | None = None
    hash: str | None = None
    expired_at: datetime | None = None
