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

    def __init__(
        self, session_factory: Callable[..., AbstractContextManager[AsyncSession]]
    ):
        self._session_factory = session_factory

    async def get_by_id(self, id: UUID) -> Model | None:
        async with self._session_factory() as session:
            stmt = select(self.model).where(self.model.id == id)
            return await session.scalar(stmt)

    async def create(self, data: dict) -> Model:
        async with self._session_factory() as session:
            stmt = insert(self.model).values(**data).returning(self.model)
            obj = await session.scalar(stmt)
            await session.commit()
            return obj

    async def update_by_id(self, id: UUID, data: dict) -> Model | None:
        async with self._session_factory() as session:
            stmt = (
                update(self.model)
                .where(self.model.id == id)
                .values(**data)
                .returning(self.model)
            )
            obj = await session.scalar(stmt)
            await session.commit()
            return obj

    async def delete_by_id(self, id: UUID) -> Model:
        async with self._session_factory() as session:
            stmt = (
                delete(self.model).where(self.model.id == id).returning(self.model.id)
            )
            obj = await session.scalar(stmt)
            await session.commit()
            return obj

    async def get_all(self, async_session: AsyncSession) -> list[Model] | None:
        async with self._session_factory() as session:
            stmt = select(self.model)
            return (await session.scalars(stmt)).all()
