import random
import string
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from shorty.config import config
from shorty.db.schemas.url import UrlCreateSchema, UrlInDB, UrlSchema, UrlUpdateSchema
from shorty.repositories.url import UrlRepository
from shorty.utils.exceptions import GoneError, InsufficientStorage, NotFoundError


class UrlService:

    def __init__(self, session: AsyncSession):
        self._session = session
        self._repository = UrlRepository(session)

    @staticmethod
    def generate_random_hash(length: int = config.app.hash_len) -> str:
        characters = string.ascii_letters.upper()
        random_hash = "".join(random.choices(characters, k=length))
        return random_hash

    async def get_url_by_id(self, url_id) -> UrlSchema:
        url = await self._repository.get_by_id(url_id)
        if not url:
            raise NotFoundError(f"url not found by id: {url_id}")
        return UrlSchema.model_validate(url, from_attributes=True)

    async def get_reserved_url_count(self) -> int:
        return await self._repository.get_reserved_count()

    async def update_url_by_id(
        self, url_id: UUID, new_url: UrlUpdateSchema
    ) -> UrlSchema:
        url = await self.get_url_by_id(url_id)
        updated_url = url.model_copy(update=new_url.model_dump(exclude_unset=True))
        updated_url = UrlInDB.model_validate(updated_url, from_attributes=True)
        return await self._repository.update_by_id(url_id, updated_url.model_dump())

    async def create_url(self, url: UrlCreateSchema) -> UrlSchema:
        if await self.get_reserved_url_count() >= config.app.get_combinations_count:
            raise InsufficientStorage("cannot allocate new hash at this time")
        url_hash = self.generate_random_hash()

        exisiting_url = await self._repository.get_url_by_hash(url_hash)

        while exisiting_url:
            if exisiting_url.expired_at <= datetime.now():  # TODO
                updated_url = UrlUpdateSchema.model_validate(url, from_attributes=True)
                updated_url.expired_at = url.expiration_time + datetime.now()
                return await self.update_url_by_id(exisiting_url.id, updated_url)
            url_hash = self.generate_random_hash()
            exisiting_url = await self._repository.get_url_by_hash(url_hash)

        url = UrlInDB(
            url=url.url, hash=url_hash, expired_at=url.expiration_time + datetime.now()
        )

        url = await self._repository.create(url.model_dump())
        return UrlSchema.model_validate(url, from_attributes=True)

    async def get_url_by_hash(self, hash: str) -> UrlSchema:
        url = await self._repository.get_url_by_hash(hash)
        if not url:
            raise NotFoundError(f"url not found by hash: {hash}")
        if url.expired_at <= datetime.now():
            raise GoneError(
                f"url hash has been expired, id: {url.id}, hash: {url.hash}"
            )
        return UrlSchema.model_validate(url, from_attributes=True)
