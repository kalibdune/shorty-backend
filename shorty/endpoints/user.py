import logging
from uuid import UUID

from fastapi import APIRouter, Depends, status

from shorty.db.schemas.user import UserCreateSchema, UserSchema, UserUpdateSchema
from shorty.endpoints.dependencies import get_session
from shorty.services.user import UserService

router = APIRouter(prefix="/user")
hash_router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreateSchema, session=Depends(get_session)):
    user_service = UserService(session)
    return await user_service.create_user(data)


@router.get("/{id}", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def get_user_by_id(id: UUID, session=Depends(get_session)):
    user_service = UserService(session)
    return await user_service.get_user_by_id(id)


@router.patch("/{id}", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def update_user(data: UserUpdateSchema, id: UUID, session=Depends(get_session)):
    user_service = UserService(session)
    return await user_service.update_user_by_id(id, data)
