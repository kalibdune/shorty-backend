import logging
from typing import Annotated

from fastapi import APIRouter, Path, status
from fastapi.responses import RedirectResponse

from shorty.db.schemas.url import UrlCreateSchema, UrlSchema
from shorty.db.session import session_manager
from shorty.services.url import UrlService

router = APIRouter(prefix="/url")
hash_router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/", response_model=UrlSchema, status_code=status.HTTP_201_CREATED)
async def create_short_url(data: UrlCreateSchema):
    async with session_manager.session() as session:
        url_service = UrlService(session)
        return await url_service.create_url(data)


@router.get("/{hash}", response_model=UrlSchema, status_code=status.HTTP_200_OK)
async def get_hash_url(
    hash: Annotated[str, Path(pattern=r"^[A-Z]{5,5}$", max_length=5)],
):
    async with session_manager.session() as session:
        url_service = UrlService(session)
        return await url_service.get_url_by_hash(hash)


@hash_router.get(
    "/{hash}", response_model=UrlSchema, status_code=status.HTTP_307_TEMPORARY_REDIRECT
)
async def redirect_on_url(
    hash: Annotated[str, Path(pattern=r"^[A-Z]{5,5}$", max_length=5)],
):
    async with session_manager.session() as session:
        url_service = UrlService(session)
        url = await url_service.get_url_by_hash(hash)
        return RedirectResponse(url.url)
