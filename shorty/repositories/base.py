from abc import ABC
from contextlib import AbstractContextManager
from typing import Callable, Generic, TypeVar
from uuid import UUID

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

Model = TypeVar("Model")


class AbstractRepository(ABC):
    async def get_by_id(self, id: UUID):
        raise NotImplementedError

    async def create(self, data: dict):
        raise NotImplementedError

    async def update_by_id(self, id: UUID, data: dict):
        raise NotImplementedError

    async def delete_by_id(self, id: UUID):
        raise NotImplementedError

    async def get_all(self, async_session: AsyncSession):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository, Generic[Model]):
    model: Model = None

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, id: UUID) -> Model | None:
        stmt = select(self.model).where(self.model.id == id)
        return await self._session.scalar(stmt)

    async def create(self, data: dict) -> Model:
        stmt = insert(self.model).values(**data).returning(self.model)
        obj = await self._session.scalar(stmt)
        await self._session.commit()
        return obj

    async def update_by_id(self, id: UUID, data: dict) -> Model | None:
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**data)
            .returning(self.model)
        )
        obj = await self._session.scalar(stmt)
        await self._session.commit()
        return obj

    async def delete_by_id(self, id: UUID) -> Model:
        stmt = delete(self.model).where(self.model.id == id).returning(self.model.id)
        obj = await self._session.scalar(stmt)
        await self._session.commit()
        return obj

    async def get_all(self) -> list[Model] | None:
        stmt = select(self.model)
        return (await self._session.scalars(stmt)).all()
