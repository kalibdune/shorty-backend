from datetime import datetime, timedelta

import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from shorty.config import config
from shorty.db.schemas.auth import TokenSchema
from shorty.repositories.user import UserRepository
from shorty.utils.enums import TokenType
from shorty.utils.exceptions import NotFoundError, UnauthorizedError
from shorty.utils.singleton import SingletonMeta


class AuthService(metaclass=SingletonMeta):

    def __init__(self):
        self._context = CryptContext(
            schemes=[config.app.encrypt_type], deprecated="auto"
        )

    def emit_new_token(self, username: str, token_type: TokenType) -> str:
        if token_type == TokenType.access:
            exp = datetime.now() + timedelta(seconds=config.app.access_token_expire)
        elif token_type == TokenType.refresh:
            exp = datetime.now() + timedelta(seconds=config.app.refresh_token_expire)
        else:
            raise Exception("Uknown TokenType")

        data = {
            "sub": username,
            "exp": exp,
            "type": token_type,
        }
        encoded_jwt = jwt.encode(
            data, config.app.secret_key, algorithm=config.app.hash_algorithm
        )
        return encoded_jwt

    async def create_tokens(
        self, session: AsyncSession, username: str, password: str
    ) -> TokenSchema:
        user_repository = UserRepository(session)
        user = await user_repository.get_by_email(username)

        if not user or not user.password:
            raise NotFoundError(f"user not found with username: {username}")

        if not self.verify_password(password, user.password):
            raise UnauthorizedError(f"incorrect password: {password}")

        access_token = self.emit_new_token(username, TokenType.access.value)
        refresh_token = self.emit_new_token(username, TokenType.refresh.value)

        return TokenSchema(access_token=access_token, refresh_token=refresh_token)

    def validate_token(self, token: str, token_type: TokenType) -> bool:
        try:
            payload = jwt.decode(
                token, config.app.secret_key, algorithms=[config.app.hash_algorithm]
            )
            username = payload.get("sub")
            token_scope = payload.get("type")
            if username is None:
                raise UnauthorizedError("username not provided")
            if token_scope != token_type:
                raise UnauthorizedError("Incorrect token type")

        except jwt.InvalidTokenError:
            raise UnauthorizedError("invalid jwt token")

        return True

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self._context.verify(plain_password, hashed_password)

    def get_hash_password(self, plain_password: str) -> str:
        return self._context.hash(plain_password)
