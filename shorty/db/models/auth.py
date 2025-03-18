from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shorty.db.models.base import Base, TimeStampMixin

if TYPE_CHECKING:
    from shorty.db.models.user import User


class Auth(Base, TimeStampMixin):
    __tablename__ = "auth"

    refresh_token: Mapped[str] = mapped_column(nullable=False)
    revoked: Mapped[bool] = mapped_column(default=False, nullable=False)
    expired_at: Mapped[datetime] = mapped_column(nullable=False)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usr.id"))

    user: Mapped["User"] = relationship(
        "User",
        back_populates="auths",
    )

    def __repr__(self) -> str:
        attrs = ", ".join(
            f"{key}={value!r}"
            for key, value in self.__dict__.items()
            if not key.startswith("_")
        )
        return f"Auth({attrs})"

    class Config:
        orm_mode = True
