import random
import string
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from shorty.config import config
from shorty.db.schemas.url import (
    UrlCreateSchema,
    UrlInDB,
    UrlPaginatedSchema,
    UrlSchema,
    UrlUpdateSchema,
)
from shorty.db.schemas.user import UserSchema
from shorty.repositories.url import UrlRepository
from shorty.services.user import UserService
from shorty.utils.exceptions import (
    GoneError,
    InsufficientStorage,
    NotFoundError,
    UserNotAuthorised,
)


@dataclass
class AvailableHashDTO:
    isunique: bool
    url_hash: str
    existing_url_id: UUID | None = None


class UrlService:

    def __init__(self, session: AsyncSession):
        self._session = session
        self._repository = UrlRepository(session)

    @staticmethod
    def _generate_random_hash(length: int = config.app.hash_len) -> str:
        characters = string.ascii_letters.upper()
        random_hash = "".join(random.choices(characters, k=length))
        return random_hash

    async def _generate_available_hash(self) -> AvailableHashDTO:
        url_hash = self._generate_random_hash()
        exisiting_url = await self._repository.get_url_by_hash(url_hash)

        while exisiting_url:
            if exisiting_url.expired_at and exisiting_url.expired_at <= datetime.now():
                return AvailableHashDTO(
                    isunique=False, existing_url_id=exisiting_url.id, url_hash=url_hash
                )
            url_hash = self._generate_random_hash()
            exisiting_url = await self._repository.get_url_by_hash(url_hash)

        return AvailableHashDTO(isunique=True, url_hash=url_hash)

    async def get_url_by_id(self, url_id) -> UrlSchema:
        url = await self._repository.get_by_id(url_id)
        if not url:
            raise NotFoundError(f"url not found by id: {url_id}")
        return UrlSchema.model_validate(url, from_attributes=True)

    async def get_paginated_urls_by_user(
        self, user_id: UUID, page: int, size: int
    ) -> UrlPaginatedSchema:
        user_service = UserService(self._session)
        await user_service.get_user_by_id(user_id)

        res = await self._repository.get_paginated(user_id, page, size)
        count, urls = res[0], res[1]
        if urls:
            return UrlPaginatedSchema(
                urls=[
                    UrlSchema.model_validate(url, from_attributes=True) for url in urls
                ],
                total_count=count,
            )
        return UrlPaginatedSchema(urls=[], total_count=count)

    async def _get_reserved_url_count(self) -> int:
        return await self._repository.get_reserved_count()

    async def update_url_by_id(
        self, url_id: UUID, new_url: UrlUpdateSchema
    ) -> UrlSchema:
        url = await self.get_url_by_id(url_id)
        updated_url = url.model_copy(update=new_url.model_dump(exclude_unset=True))
        updated_url_dict = updated_url.model_dump()
        updated_url_dict["url"] = str(updated_url_dict["url"])
        updated_url = UrlInDB.model_validate(updated_url_dict)
        return await self._repository.update_by_id(url_id, updated_url.model_dump())

    async def create_url(
        self, url: UrlCreateSchema, user: UserSchema | None
    ) -> UrlSchema:
        if not user and not url.expiration_time:
            raise UserNotAuthorised(
                "cannot create unlimited time without provided user"
            )

        if (
            not user
            and url.expiration_time
            and url.expiration_time
            > datetime.now() + timedelta(seconds=config.app.temporary_url_lifetime)
        ):
            raise UserNotAuthorised(
                "cannot create url with expiration time above than temporary_url_lifetime"
            )

        if await self._get_reserved_url_count() >= config.app.get_combinations_count:
            raise InsufficientStorage("cannot allocate new hash at this time")

        hash_dto = await self._generate_available_hash()

        if not hash_dto.isunique:
            updated_url = UrlUpdateSchema.model_validate(url, from_attributes=True)
            updated_url.expired_at = url.expiration_time
            return await self.update_url_by_id(hash_dto.existing_url_id, updated_url)

        url = UrlInDB(
            url=str(url.url),
            hash=hash_dto.url_hash,
            expired_at=url.expiration_time,
            user_id=user.id if user else None,
        )

        url = await self._repository.create(url.model_dump())
        return UrlSchema.model_validate(url, from_attributes=True)

    async def get_url_by_hash(self, hash: str) -> UrlSchema:
        url = await self._repository.get_url_by_hash(hash)
        if not url:
            raise NotFoundError(f"url not found by hash: {hash}")
        if url.expired_at and url.expired_at <= datetime.now():
            raise GoneError(
                f"url hash has been expired, id: {url.id}, hash: {url.hash}"
            )
        return UrlSchema.model_validate(url, from_attributes=True)
