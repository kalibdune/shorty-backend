import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from shorty.db.schemas.auth import RevokedTokensSchema
from shorty.endpoints.dependencies import OAuth, get_session
from shorty.services.auth import AuthService

router = APIRouter(prefix="/token")

logger = logging.getLogger(__name__)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    resp: Response,
    session=Depends(get_session),
):
    auth_service = AuthService(session)
    tokens = await auth_service.create_tokens(form_data.username, form_data.password)
    resp.set_cookie(
        "access_token", tokens.access_token, httponly=True, samesite="strict"
    )
    resp.set_cookie(
        "refresh_token",
        tokens.refresh_token,
        httponly=True,
        samesite="strict",
        expires=None,
    )


@router.post("/refresh", status_code=status.HTTP_201_CREATED)
async def refresh_tokens(
    response: Response,
    request: Request,
    session=Depends(get_session),
):

    auth_service = AuthService(session)
    refresh_token = request.cookies.get("refresh_token")

    token = await auth_service.reemit_access_token(refresh_token)
    response.set_cookie("access_token", token, httponly=True, samesite="strict")


@router.post(
    "/revoke", response_model=RevokedTokensSchema, status_code=status.HTTP_201_CREATED
)
async def revoke_tokens(user: OAuth, session=Depends(get_session)):
    auth_service = AuthService(session)
    return await auth_service.revoke_tokens_by_user_id(user)
