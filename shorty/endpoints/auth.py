import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from shorty.db.schemas.auth import RevokedTokensSchema
from shorty.db.schemas.user import UserSchema
from shorty.endpoints.dependencies import OAuth, get_session
from shorty.services.auth import AuthService
from shorty.services.user import UserService

router = APIRouter(prefix="/token")

logger = logging.getLogger(__name__)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserSchema)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    resp: Response,
    session=Depends(get_session),
):
    auth_service = AuthService(session)
    user_service = UserService(session)

    user = await user_service.get_user_by_email(form_data.username)
    
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

    return user


@router.post("/refresh/", status_code=status.HTTP_201_CREATED)
async def refresh_tokens(
    response: Response,
    request: Request,
    session=Depends(get_session),
):

    auth_service = AuthService(session)
    refresh_token = request.cookies.get("refresh_token")

    token = await auth_service.reemit_access_token(refresh_token)
    response.set_cookie("access_token", token, httponly=True, samesite="strict")


@router.delete(
    "/revoke/", response_model=RevokedTokensSchema, status_code=status.HTTP_201_CREATED
)
async def revoke_tokens(user: OAuth, session=Depends(get_session)):
    auth_service = AuthService(session)
    return await auth_service.revoke_tokens_by_user_id(user)


@router.delete("/logout/", response_model=None, status_code=status.HTTP_200_OK)
async def logout_and_delete_tokens(
    auth: OAuth, response: Response, request: Request, session=Depends(get_session)
):
    auth_service = AuthService(session)

    refresh_token = request.cookies.get("refresh_token")

    response.delete_cookie("access_token", httponly=True, samesite="strict")
    response.delete_cookie("refresh_token", httponly=True, samesite="strict")

    await auth_service.revoke_refresh_token(refresh_token)
