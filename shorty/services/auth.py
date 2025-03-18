from datetime import datetime, timedelta
from uuid import UUID

import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from shorty.config import config
from shorty.db.schemas.auth import (
    RefreshTokenCreateSchema,
    RefreshTokenSchema,
    TokensSchema,
)
from shorty.repositories.auth import AuthRepository
from shorty.repositories.user import UserRepository
from shorty.utils.enums import TokenType
from shorty.utils.exceptions import GoneError, NotFoundError, UnauthorizedError
from shorty.utils.singleton import SingletonMeta


class AuthService(metaclass=SingletonMeta):

    def __init__(self, session: AsyncSession):
        self._context = CryptContext(
            schemes=[config.app.encrypt_type], deprecated="auto"
        )
        self._session = session
        self._repository = AuthRepository(self._session)

    def _emit_new_token(
        self, username: str, token_type: TokenType, exp: datetime | None = None
    ) -> str:
        if not exp:
            if token_type == TokenType.access:
                exp = datetime.now() + timedelta(seconds=config.app.access_token_expire)
            elif token_type == TokenType.refresh:
                exp = datetime.now() + timedelta(
                    seconds=config.app.refresh_token_expire
                )
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

    def emit_access_token(self, username: str) -> str:
        return self._emit_new_token(username, TokenType.access.value)

    async def emit_refresh_token(self, username: str, user_id: UUID) -> str:
        exp = datetime.now() + timedelta(seconds=config.app.refresh_token_expire)
        token = RefreshTokenCreateSchema(
            expired_at=exp,
            refresh_token=self._emit_new_token(username, TokenType.refresh.value, exp),
            user_id=user_id,
        )
        await self.create_refresh_token(token)
        return token.refresh_token

    async def create_refresh_token(
        self, token: RefreshTokenCreateSchema
    ) -> RefreshTokenSchema:
        token = await self._repository.create(token.model_dump())
        return RefreshTokenSchema.model_validate(token, from_attributes=True)

    async def get_token_object_by_token(self, token: str) -> RefreshTokenSchema:
        data = await self._repository.get_by_token(token)
        if not data:
            raise NotFoundError("token not found")
        if data.expired_at <= datetime.now():
            await self._repository.update_by_id(data.id, {"revoked": True})
            raise GoneError("token has been expired")
        return RefreshTokenSchema.model_validate(data, from_attributes=True)

    async def reemit_access_token(self, refresh_token: str | None) -> str:
        if not refresh_token:
            raise NotFoundError("token not found in cookies")

        self.validate_token(refresh_token, TokenType.refresh)

        data = await self.get_token_object_by_token(refresh_token)

        user_repository = UserRepository(self._session)
        user = await user_repository.get_by_id(data.user_id)
        if not user:
            raise NotFoundError(f"user not found by id: {data.user_id}")

        return self.emit_access_token(user.email)

    async def create_tokens(self, username: str, password: str) -> TokensSchema:
        user_repository = UserRepository(self._session)
        user = await user_repository.get_by_email(username)

        if not user or not user.password:
            raise NotFoundError(f"user not found with username: {username}")

        if not self.verify_password(password, user.password):
            raise UnauthorizedError(f"incorrect password: {password}")

        access_token = self.emit_access_token(username)
        refresh_token = await self.emit_refresh_token(username, user.id)

        return TokensSchema(access_token=access_token, refresh_token=refresh_token)

    def validate_token(self, token: str | None, token_type: TokenType) -> bool:
        if not token:
            raise UnauthorizedError("token not provided")
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
