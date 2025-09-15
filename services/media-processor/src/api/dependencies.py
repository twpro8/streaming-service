from typing import Annotated

from fastapi import Depends, Query
from fastapi.requests import Request
from pydantic import BaseModel

from src.exceptions import NoTokenHTTPException, PermissionDeniedHTTPException
from src.factories.services_factories import (
    VideoServiceFactory,
    ImageServiceFactory,
    AuthServiceFactory,
)
from src.services.auth import AuthService
from src.services.images import ImageService
from src.services.videos import VideoService


VideoServiceDep = Annotated[VideoService, Depends(VideoServiceFactory.video_service_factory)]
ImageServiceDep = Annotated[ImageService, Depends(ImageServiceFactory.image_service_factory)]
AuthServiceDep = Annotated[AuthService, Depends(AuthServiceFactory.auth_service_factory)]


def get_token(request: Request) -> str:
    token = request.cookies.get("access_token", None)
    if not token:
        raise NoTokenHTTPException
    return token


def get_admin(auth_service: AuthServiceDep, token: str = Depends(get_token)):
    data = auth_service.decode_token(token)
    is_admin = data.get("is_admin", False)

    if isinstance(is_admin, str):
        is_admin = is_admin.lower() == "true"

    if not is_admin:
        raise PermissionDeniedHTTPException


AdminDep = Depends(get_admin)


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(default=1, ge=1)]
    per_page: Annotated[int | None, Query(default=5, ge=1, le=30)]


PaginationDep = Annotated[PaginationParams, Depends()]
