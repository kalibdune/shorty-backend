import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from shorty.db.schemas.user import UserCreateSchema, UserSchema, UserUpdateSchema
from shorty.endpoints.dependencies import OAuth, get_session
from shorty.services.auth import AuthService
from shorty.services.user import UserService

router = APIRouter(prefix="/user")
hash_router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreateSchema, response: Response, session=Depends(get_session)
):
    user_service = UserService(session)
    auth_service = AuthService(session)

    user = await user_service.create_user(data)

    access_token = auth_service.emit_access_token(user.email)
    refresh_token = await auth_service.emit_refresh_token(user.email, user.id)

    response.set_cookie("access_token", access_token, httponly=True)
    response.set_cookie("refresh_token", refresh_token, httponly=True)

    return user


@router.get("/{id}/", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def get_user_by_id(id: UUID, auth: OAuth, session=Depends(get_session)):
    user_service = UserService(session)
    return await user_service.get_user_by_id(id)


@router.patch("/{id}/", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def update_user(
    data: UserUpdateSchema, auth: OAuth, id: UUID, session=Depends(get_session)
):
    user_service = UserService(session)
    return await user_service.update_user_by_id(id, data)
