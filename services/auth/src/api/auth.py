from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Body, Depends

from src.exceptions import (
    UserNotFoundException,
    UserNotFoundHTTPException,
    InvalidRefreshTokenException,
    InvalidRefreshTokenHTTPException,
    RefreshTokenNotFoundException,
    RefreshTokenNotFoundHTTPException,
)
from src.factories.service import ServiceFactory
from src.services.auth import AuthService


v1_router = APIRouter(prefix="/v1/auth", tags=["auth"])


@v1_router.post("/refresh")
async def refresh_token(
    service: Annotated[AuthService, Depends(ServiceFactory.auth_service_factory)],
    refresh_token: str = Body(embed=True),
):
    try:
        tokens = await service.refresh_token(refresh_token)
    except InvalidRefreshTokenException:
        raise InvalidRefreshTokenHTTPException
    except RefreshTokenNotFoundException:
        raise RefreshTokenNotFoundHTTPException
    except UserNotFoundException:
        raise UserNotFoundHTTPException
    return {"status": "ok", "data": tokens}


@v1_router.post("/logout")
async def logout(
    service: Annotated[AuthService, Depends(ServiceFactory.auth_service_factory)],
    refresh_token: str = Body(embed=True),
):
    try:
        await service.revoke_refresh_token(refresh_token)
    except InvalidRefreshTokenException:
        raise InvalidRefreshTokenHTTPException
    except RefreshTokenNotFoundException:
        raise RefreshTokenNotFoundHTTPException
    return {"status": "ok"}
