from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator


class UrlRedirectBaseSchema(BaseModel):
    url_id: UUID


class UrlRedirectCreateSchema(UrlRedirectBaseSchema): ...


class UrlRedirectSchema(UrlRedirectBaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime


class UrlRedirectStatisticSchema(BaseModel):
    url_redirections: list[UrlRedirectSchema]
    count: int


class UrlRedirectRequestSchema(BaseModel):
    started_at: datetime
    ended_at: datetime

    @field_validator("started_at", "ended_at")
    def parse_datetime(cls, value):
        if value:
            return value.replace(tzinfo=None)
        return value
