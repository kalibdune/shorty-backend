from typing import Annotated

from fastapi import Depends, Path
from fastapi.security import OAuth2PasswordBearer

from shorty.config import config
from shorty.db.schemas.user import UserSchema
from shorty.db.session import session_manager
from shorty.services.auth import AuthService
from shorty.utils.enums import TokenType

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")
hash_len = config.app.hash_len

HashType = Annotated[
    str, Path(regex=r"^[A-Z]{{{0}}}$".format(hash_len), max_length=hash_len)
]


async def get_session():
    async with session_manager.session() as session:
        yield session


async def check_auth(token: str = Depends(oauth2_scheme)) -> UserSchema:
    return AuthService().validate_token(token, TokenType.access)


OAuth = Annotated[UserSchema, Depends(check_auth)]
