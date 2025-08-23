from datetime import datetime
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from shorty.db.models.url_redirect import UrlRedirect
from shorty.repositories.base import SQLAlchemyRepository


class UrlRedirectRepository(SQLAlchemyRepository):
    model = UrlRedirect

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_redirections_by_url_id(
        self, url_id: UUID, started_at: datetime, ended_at: datetime
    ) -> tuple[int, list[UrlRedirect]]:
        stmt1 = (
            select(self.model)
            .where(self.model.url_id == url_id)
            .where(self.model.created_at <= ended_at)
            .where(self.model.created_at >= started_at)
            .order_by(desc(self.model.created_at))
        )
        result = (await self._session.scalars(stmt1)).all()

        return len(result), result
