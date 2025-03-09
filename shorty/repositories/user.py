from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shorty.db.models.user import User
from shorty.repositories.base import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    model = User

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(self.model).where(self.model.email == email)
        return await self._session.scalar(stmt)
