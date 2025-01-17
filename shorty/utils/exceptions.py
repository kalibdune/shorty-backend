import logging

from fastapi.exceptions import HTTPException
from starlette import status

logger = logging.getLogger(__name__)


class BaseAPIException(HTTPException):
    status_code: status
    error: str

    def __init__(self, detail: str) -> None:
        self.detail = detail

    def __repr__(self) -> str:
        return f"Error: {self.error}, status: {self.status_code}, detail: {self.detail}"


class NotFoundError(BaseAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    error = "Not found"


class AlreadyExistError(BaseAPIException):
    status_code = status.HTTP_409_CONFLICT
    error = "Already exist"


class UserNotAuthorised(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    error = "User is not authorized"


class GoneError(BaseAPIException):
    status_code = status.HTTP_410_GONE
    error = "expired or inactive"


class UnAvailableError(BaseAPIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error = "service unaviable"


class BadRequestError(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    error = "bad request"
