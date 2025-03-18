from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shorty.db.models.auth import Auth
from shorty.repositories.base import SQLAlchemyRepository


class AuthRepository(SQLAlchemyRepository):
    model = Auth

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_token(self, token: str) -> Auth | None:
        stmt = select(self.model).where(
            self.model.refresh_token == token and self.model.revoked == False
        )
        return await self._session.scalar(stmt)
