from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shorty.db.models.base import Base, TimeStampMixin

if TYPE_CHECKING:
    from shorty.db.models.url import Url


class UrlRedirect(Base, TimeStampMixin):
    __tablename__ = "url_redirect"

    url_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("url.id", ondelete="CASCADE"), nullable=False
    )

    url: Mapped["Url"] = relationship("Url", back_populates="url_redirects")

    def __repr__(self) -> str:
        attrs = ", ".join(
            f"{key}={value!r}"
            for key, value in self.__dict__.items()
            if not key.startswith("_")
        )
        return f"UrlRedirect({attrs})"

    class Config:
        orm_mode = True
