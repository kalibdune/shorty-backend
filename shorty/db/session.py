import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from shorty.config import config

logger = logging.getLogger(__name__)


class SessionManager:

    def __init__(self, db_dsn: str, echo: bool = False):
        self._engine = create_async_engine(
            url=db_dsn,
            echo=echo,
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            logger.exception("Session rollback because of exception")
            await session.rollback()
            raise
        finally:
            await session.close()


session_manager = SessionManager(config.postgres.get_dsn, config.postgres.debug)
