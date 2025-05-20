import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import RedirectResponse

from shorty.db.schemas.url import (
    UrlCreateSchema,
    UrlPaginatedSchema,
    UrlSchema,
    UrlUpdateSchema,
)
from shorty.db.schemas.url_redirect import (
    UrlRedirectCreateSchema,
    UrlRedirectRequestSchema,
    UrlRedirectStatisticSchema,
)
from shorty.endpoints.dependencies import (
    HashType,
    OAuth,
    UnstrictedOAuth,
    get_session,
    get_session_repeatable_read,
)
from shorty.services.url import UrlService
from shorty.services.url_redirect import UrlRedirectService

router = APIRouter(prefix="/url")
hash_router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/", response_model=UrlSchema, status_code=status.HTTP_201_CREATED)
async def create_short_url(
    data: UrlCreateSchema, user: UnstrictedOAuth, session=Depends(get_session)
):
    url_service = UrlService(session)
    return await url_service.create_url(data, user)


@router.get("/{hash}/", response_model=UrlSchema, status_code=status.HTTP_200_OK)
async def get_hash_url(
    hash: HashType,
    auth: OAuth,
    session=Depends(get_session),
):
    url_service = UrlService(session)
    url_redirect_service = UrlRedirectService(session)

    url = await url_service.get_url_by_hash(hash)
    await url_redirect_service.create_redirection(
        UrlRedirectCreateSchema(url_id=url.id)
    )

    return await url_service.get_url_by_hash(hash)


@router.get(
    "/user/{user_id}/",
    response_model=UrlPaginatedSchema,
    status_code=status.HTTP_200_OK,
)
async def get_urls_by_user(
    user_id: UUID,
    auth: OAuth,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    session=Depends(get_session_repeatable_read),
):
    url_service = UrlService(session)
    return await url_service.get_paginated_urls_by_user(user_id, page, size)


@hash_router.get(
    "/{hash}/", response_model=None, status_code=status.HTTP_307_TEMPORARY_REDIRECT
)
async def redirect_on_url(
    hash: HashType,
    session=Depends(get_session),
):
    url_service = UrlService(session)
    url_redirect_service = UrlRedirectService(session)

    url = await url_service.get_url_by_hash(hash)
    await url_redirect_service.create_redirection(
        UrlRedirectCreateSchema(url_id=url.id)
    )

    return RedirectResponse(url.url)


@router.post(
    "/statistic/{url_id}",
    response_model=UrlRedirectStatisticSchema,
    status_code=status.HTTP_200_OK,
)
async def get_statistic_by_url(
    url_id: UUID,
    data: UrlRedirectRequestSchema,
    auth: OAuth,
    session=Depends(get_session_repeatable_read),
):
    url_redirect_service = UrlRedirectService(session)
    return await url_redirect_service.get_redirects_by_url_id(url_id, data)


@router.put("/{url_id}/", response_model=UrlSchema, status_code=status.HTTP_200_OK)
async def update_url_by_id(
    url_id: UUID, data: UrlUpdateSchema, auth: OAuth, session=Depends(get_session)
):
    url_service = UrlService(session)
    return await url_service.update_url_by_id(url_id, data)
