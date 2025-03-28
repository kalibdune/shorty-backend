import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import RedirectResponse

from shorty.db.schemas.url import UrlCreateSchema, UrlSchema
from shorty.endpoints.dependencies import HashType, OAuth, get_session
from shorty.services.url import UrlService

router = APIRouter(prefix="/url")
hash_router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/", response_model=UrlSchema, status_code=status.HTTP_201_CREATED)
async def create_short_url(data: UrlCreateSchema, session=Depends(get_session)):
    url_service = UrlService(session)
    return await url_service.create_url(data)


@router.get(
    "/{user_id}/", response_model=list[UrlSchema], status_code=status.HTTP_200_OK
)
async def get_urls_by_user(
    user_id: UUID,
    auth: OAuth,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    session=Depends(get_session),
):
    url_service = UrlService(session)
    return await url_service.get_paginated_urls_by_user(user_id, page, size)


@router.get("/{hash}/", response_model=UrlSchema, status_code=status.HTTP_200_OK)
async def get_hash_url(
    hash: HashType,
    auth: OAuth,
    session=Depends(get_session),
):
    url_service = UrlService(session)
    return await url_service.get_url_by_hash(hash)


@hash_router.get(
    "/{hash}/", response_model=UrlSchema, status_code=status.HTTP_307_TEMPORARY_REDIRECT
)
async def redirect_on_url(
    hash: HashType,
    session=Depends(get_session),
):
    url_service = UrlService(session)
    url = await url_service.get_url_by_hash(hash)
    return RedirectResponse(url.url)
