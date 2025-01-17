from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shorty.db.models.url import Url
from shorty.repositories.base import SQLAlchemyRepository


class UrlRepository(SQLAlchemyRepository):
    model = Url

    def __init__(
        self, session_factory: Callable[..., AbstractContextManager[AsyncSession]]
    ) -> None:
        super().__init__(session_factory)

    async def get_url_by_hash(self, hash: str) -> Url | None:
        async with self._session_factory() as session:
            stmt = select(self.model).where(self.model.hash == hash)
            return await session.scalar(stmt)
