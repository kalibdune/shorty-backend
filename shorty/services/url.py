import random
import string
from datetime import datetime

from shorty.db.schemas.url import UrlCreateSchema, UrlInDB, UrlSchema
from shorty.repositories.url import UrlRepository
from shorty.utils.exceptions import GoneError, NotFoundError


class UrlService:

    def __init__(self, url_repository: UrlRepository):
        self._repository: UrlRepository = url_repository

    @staticmethod
    def generate_random_hash(length: int = 5) -> str:
        characters = string.ascii_letters.upper()
        random_hash = "".join(random.choices(characters, k=length))
        return random_hash

    async def create_url(self, url: UrlCreateSchema) -> UrlSchema:
        url_hash = self.generate_random_hash()

        while await self._repository.get_url_by_hash(url_hash):
            url_hash = self.generate_random_hash()

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
            raise GoneError(f"hash has been expired, id: {url.id}, hash: {url.hash}")
        return UrlSchema.model_validate(url, from_attributes=True)
