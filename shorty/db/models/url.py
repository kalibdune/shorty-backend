from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shorty.db.models.base import Base, TimeStampMixin

if TYPE_CHECKING:
    from shorty.db.models.user import User


class Url(Base, TimeStampMixin):
    __tablename__ = "url"

    url: Mapped[str] = mapped_column(nullable=False)
    hash: Mapped[str] = mapped_column(
        String(length=5), nullable=False, unique=True, index=True
    )
    expired_at: Mapped[datetime] = mapped_column(nullable=True)

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usr.id"), nullable=True
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="urls",
    )

    def __repr__(self) -> str:
        attrs = ", ".join(
            f"{key}={value!r}"
            for key, value in self.__dict__.items()
            if not key.startswith("_")
        )
        return f"Url({attrs})"

    class Config:
        orm_mode = True
