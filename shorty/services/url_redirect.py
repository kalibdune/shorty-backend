from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from shorty.db.schemas.url_redirect import (
    UrlRedirectCreateSchema,
    UrlRedirectRequestSchema,
    UrlRedirectSchema,
    UrlRedirectStatisticSchema,
)
from shorty.repositories.url_redirect import UrlRedirectRepository
from shorty.services.url import UrlService


class UrlRedirectService:

    def __init__(self, session: AsyncSession):
        self._session = session
        self._repository = UrlRedirectRepository(session)

    async def get_redirects_by_url_id(
        self, url_id: UUID, data: UrlRedirectRequestSchema
    ) -> UrlRedirectStatisticSchema:
        url_service = UrlService(self._session)
        await url_service.get_url_by_id(url_id)

        res = await self._repository.get_redirections_by_url_id(
            url_id, data.started_at, data.ended_at
        )
        count, redirections = res[0], res[1]

        if redirections:
            return UrlRedirectStatisticSchema(
                url_redirections=[
                    UrlRedirectSchema.model_validate(redirect, from_attributes=True)
                    for redirect in redirections
                ],
                count=count,
            )
        return UrlRedirectStatisticSchema(url_redirections=[], count=count)

    async def create_redirection(
        self, data: UrlRedirectCreateSchema
    ) -> UrlRedirectSchema:
        return UrlRedirectSchema.model_validate(
            await self._repository.create(data.model_dump()), from_attributes=True
        )
