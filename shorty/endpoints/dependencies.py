from typing import Annotated

from fastapi import Path

from shorty.config import config
from shorty.db.session import session_manager

hash_len = config.app.hash_len


async def get_session():
    async with session_manager.session() as session:
        yield session


HashType = Annotated[
    str, Path(pattern=rf"^[A-Z]{hash_len,hash_len}$", max_length=hash_len)
]
