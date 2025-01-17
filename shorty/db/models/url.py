from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from shorty.db.models.base import Base, TimeStampMixin


class Url(Base, TimeStampMixin):
    __tablename__ = "url"

    url: Mapped[str] = mapped_column(nullable=False)
    hash: Mapped[str] = mapped_column(
        String(length=5), nullable=False, unique=True, index=True
    )
    expired_at: Mapped[datetime] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return f"""Url(id={self.id}, short_id={self.hash}, epired_at={self.expired_at}, created_at={self.created_at}, id={self.id})"""

    class Config:
        orm_mode = True
