from uuid import UUID

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from shorty.db.schemas.user import UserCreateSchema, UserSchema, UserUpdateSchema
from shorty.repositories.user import UserRepository
from shorty.services.auth import AuthService
from shorty.utils.exceptions import AlreadyExistError, NotFoundError


class UserService:

    def __init__(self, session: AsyncSession):
        self._session = session
        self._repository = UserRepository(session)

    async def get_user_by_id(self, user_id: UUID) -> UserSchema:
        user = await self._repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError(f"user_id: {user_id}")
        return UserSchema.model_validate(user, from_attributes=True)

    async def get_user_by_email(self, email: EmailStr) -> UserSchema:
        user = await self._repository.get_by_email(email)
        if user is None:
            raise NotFoundError(f"email: {email}")
        return UserSchema.model_validate(user, from_attributes=True)

    async def create_user(self, user: UserCreateSchema) -> UserSchema:
        db_user = await self._repository.get_by_email(str(user.email))
        if db_user:
            raise AlreadyExistError(f"user already exist. user_id: {db_user.id}")
        auth_service = AuthService()
        user.password = auth_service.get_hash_password(user.password)
        user = await self._repository.create(user.model_dump())

        return UserSchema.model_validate(user, from_attributes=True)

    async def update_user_by_id(
        self, user_id: UUID, new_user: UserUpdateSchema
    ) -> UserSchema:
        user = await self.get_user_by_id(user_id)

        for key, value in new_user.model_dump(exclude_unset=True).items():
            setattr(user, key, value)

        user = await self._repository.update_by_id(user_id, user.model_dump())
        return UserSchema.model_validate(user, from_attributes=True)
