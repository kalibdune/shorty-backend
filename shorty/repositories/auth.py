from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from shorty.db.models.auth import Auth
from shorty.repositories.base import SQLAlchemyRepository


class AuthRepository(SQLAlchemyRepository):
    model = Auth

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_token(self, token: str) -> Auth | None:
        stmt = (
            select(self.model)
            .where(self.model.refresh_token == token)
            .where(self.model.revoked == False)
        )
        return await self._session.scalar(stmt)

    async def revoke_tokens_by_user_id(self, user_id: UUID) -> int:
        stmt1 = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.user_id == user_id)
            .where(self.model.revoked == False)
        )

        stmt2 = (
            update(self.model)
            .where(self.model.user_id == user_id)
            .where(self.model.revoked == False)
            .values(revoked=True)
        )
        count = (await self._session.execute(stmt1)).scalar_one()
        await self._session.execute(stmt2)
        await self._session.commit()
        return count
