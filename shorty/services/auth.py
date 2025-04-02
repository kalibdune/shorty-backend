from datetime import datetime, timedelta
from uuid import UUID

import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from shorty.config import config
from shorty.db.schemas.auth import (
    RefreshTokenCreateSchema,
    RefreshTokenSchema,
    RevokedTokensSchema,
    TokensSchema,
)
from shorty.db.schemas.user import UserSchema
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

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self._context.verify(plain_password, hashed_password)

    def get_hash_password(self, plain_password: str) -> str:
        return self._context.hash(plain_password)

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

    async def revoke_refresh_token(self, token: str) -> None:
        if not await self._repository.get_by_token(token):
            raise NotFoundError("refresh token not foud")
        await self._repository.revoke_refresh_token_by_token(token)

    async def revoke_tokens_by_user_id(self, user: UserSchema) -> RevokedTokensSchema:
        count = await self._repository.revoke_tokens_by_user_id(user.id)
        return RevokedTokensSchema(revoked_count=count)

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

        await self.validate_token(refresh_token, TokenType.refresh)
        await self.get_token_object_by_token(refresh_token)

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

    async def validate_token(self, token: str, token_type: TokenType) -> UserSchema:
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

        user_repository = UserRepository(self._session)
        user = await user_repository.get_by_email(username)
        if not user:
            raise NotFoundError(f"user not found with email: {username}")
        return UserSchema.model_validate(user, from_attributes=True)
