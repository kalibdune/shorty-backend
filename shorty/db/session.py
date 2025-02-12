import logging
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from shorty.config import config

logger = logging.getLogger(__name__)


class SessionManager:

    def __init__(self, db_dsn: str, echo: bool = False, is_async=True):
        self.is_async = is_async
        if is_async:
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
        else:
            self._engine = create_engine(
                url=db_dsn,
                echo=echo,
            )
            self._session_factory = sessionmaker(
                self._engine,
                autoflush=False,
                autocommit=False,
                expire_on_commit=False,
                class_=Session,
            )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        if not self.is_async:
            raise Exception("you are using async context manager via sync engine")
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            logger.exception("Session rollback because of exception")
            await session.rollback()
            raise
        finally:
            await session.close()

    @contextmanager
    def sync_session(self) -> Generator[Session, None, None]:
        if self.is_async:
            raise Exception("you are using sync context manager via async engine")
        session = self._session_factory()
        try:
            yield session
        except Exception:
            logger.exception("Session rollback because of exception")
            session.rollback()
            raise
        finally:
            session.close()


session_manager = SessionManager(config.postgres.get_dsn, config.postgres.debug)
