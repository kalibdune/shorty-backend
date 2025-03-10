import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from shorty.db.schemas.auth import TokenSchema
from shorty.endpoints.dependencies import get_session
from shorty.services.auth import AuthService

router = APIRouter(prefix="/token")

logger = logging.getLogger(__name__)


@router.post("/", response_model=TokenSchema, status_code=status.HTTP_200_OK)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session=Depends(get_session),
):
    auth_service = AuthService()
    return await auth_service.create_token(
        session, form_data.username, form_data.password
    )
