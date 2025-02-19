from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from shorty.db.models.url import Url
from shorty.repositories.base import SQLAlchemyRepository


class UrlRepository(SQLAlchemyRepository):
    model = Url

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_url_by_hash(self, hash: str) -> Url | None:
        stmt = select(self.model).where(self.model.hash == hash)
        return await self._session.scalar(stmt)

    async def get_reserved_count(self) -> int:
        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.expired_at > func.now())
        )
        result = await self._session.scalar(stmt)
        return result
