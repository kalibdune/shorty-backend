from sqlalchemy.ext.asyncio import AsyncSession

from shorty.db.models.auth import Auth
from shorty.repositories.base import SQLAlchemyRepository


class AuthRepository(SQLAlchemyRepository):
    model = Auth

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
