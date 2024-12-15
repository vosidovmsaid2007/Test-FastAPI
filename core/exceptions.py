from typing import Self

from fastapi import status
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, Field


class APIExceptionModel(BaseModel):
    detail: str = Field(..., description="Текст ошибки")


class APIException(HTTPException):
    model: APIExceptionModel

    def __init__(self, *args: list, **kwargs: dict) -> None:
        super().__init__(*args, **kwargs)
        self.model = APIExceptionModel(detail=self.detail)

    def schema(self) -> dict:
        return {
            "model": self.model.__class__,
            "content": {
                "application/json": {
                    "example": {"detail": self.detail},
                },
            },
        }

    def format(self, *args: list, **kwargs: dict) -> Self:
        self.detail = self.detail.format(*args, **kwargs)
        return self


def make_schemas(*args: list) -> dict:
    d = {}
    for arg in args:
        if isinstance(arg, APIException):
            d[arg.status_code] = arg.schema()
    return d

NOT_AUTHENTICATED = APIException(status.HTTP_406_NOT_ACCEPTABLE, "Not authenticated. Invalid authorization data or token may be expired")
USER_ALREADY_EXISTS = APIException(status.HTTP_409_CONFLICT, "User with such credentials already exists")
INVALID_PASSWORD = APIException(status.HTTP_403_FORBIDDEN, "The password is invalid!")
HAS_NO_PERMISSION = APIException(status.HTTP_403_FORBIDDEN, "User has no permission to perform this action")
USER_NOT_FOUND = APIException(status.HTTP_404_NOT_FOUND, "User with such credentials was not found")
DATE_FORMAT_INVALID = APIException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Wrong date format! Try YYYY-MM-DD.")
PASSWORDS_DONT_MATCH = APIException(status.HTTP_409_CONFLICT, "Passwords do not match!")
SHOULDNT_BLOCK_YOURSELF = APIException(status.HTTP_418_IM_A_TEAPOT, "Probably shouldn't block yourself.")
ONLY_ROOT_CAN_MAKE_ITSELF = APIException(status.HTTP_400_BAD_REQUEST, "Only root user can make another root.")
CONFIRM_LINK_NOT_SENT = APIException(status.HTTP_400_BAD_REQUEST, "Confirmation link was not sent. Please, try again.")
TOKEN_NOT_FOUND = APIException(status.HTTP_404_NOT_FOUND, "Token not found or already confirmed")