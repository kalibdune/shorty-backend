from typing import Annotated

from fastapi import Depends, Path, Request

from shorty.config import config
from shorty.db.schemas.user import UserSchema
from shorty.db.session import session_manager
from shorty.services.auth import AuthService
from shorty.utils.enums import TokenType
from shorty.utils.exceptions import UnauthorizedError

hash_len = config.app.hash_len

HashType = Annotated[
    str, Path(regex=r"^[A-Z]{{{0}}}$".format(hash_len), max_length=hash_len)
]


async def get_session():
    async with session_manager.session() as session:
        yield session


async def get_session_repeatable_read():
    async with session_manager.session(isolation_level="REPEATABLE READ") as session:
        yield session


async def check_auth(request: Request, session=Depends(get_session)) -> UserSchema:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise UnauthorizedError("token not provided")
    return await AuthService(session).validate_token(access_token, TokenType.access)


async def res_check_auth(
    request: Request, session=Depends(get_session)
) -> UserSchema | None:
    try:
        return await check_auth(request, session)
    except:
        return None


OAuth = Annotated[UserSchema, Depends(check_auth)]
UnstrictedOAuth = Annotated[UserSchema | None, Depends(res_check_auth)]
