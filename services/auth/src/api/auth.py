from typing import Annotated

from fastapi import APIRouter
from fastapi.responses import Response
from fastapi.params import Depends

from src.api.dependencies import ClientInfoDep, RefreshTokenDep
from src.exceptions import (
    UserNotFoundException,
    UserNotFoundHTTPException,
    InvalidRefreshTokenException,
    InvalidRefreshTokenHTTPException,
    RefreshTokenNotFoundException,
    NoRefreshTokenHTTPException,
)
from src.factories.service import ServiceFactory
from src.schemas.users import UserAddRequestDTO, UserLoginDTO
from src.services.auth import AuthService


v1_router = APIRouter(prefix="/v1/auth", tags=["auth"])


@v1_router.post("/login")
async def login(
    service: Annotated[AuthService, Depends(ServiceFactory.auth_service_factory)],
    user: UserLoginDTO,
    client_info: ClientInfoDep,
    response: Response,
):
    access, refresh = await service.login(
        email=user.email,
        password=user.password,
        client_info=client_info,
    )
    response.set_cookie("access_token", access, httponly=True)
    response.set_cookie("refresh_token", refresh, httponly=True, path="/v1/auth/refresh")
    return {"status": "ok"}


@v1_router.post("/signup")
async def signup(
    service: Annotated[AuthService, Depends(ServiceFactory.auth_service_factory)],
    user_data: UserAddRequestDTO,
):
    await service.register(user_data)
    return {"status": "ok"}


@v1_router.post("/refresh")
async def refresh_token(
    service: Annotated[AuthService, Depends(ServiceFactory.auth_service_factory)],
    response: Response,
    client: ClientInfoDep,
    refresh_token_data: RefreshTokenDep,
):
    try:
        access, refresh = await service.refresh_token(refresh_token_data, client)
    except InvalidRefreshTokenException:
        raise InvalidRefreshTokenHTTPException
    except RefreshTokenNotFoundException:
        raise NoRefreshTokenHTTPException
    except UserNotFoundException:
        raise UserNotFoundHTTPException
    response.set_cookie("access_token", access, httponly=True)
    response.set_cookie("refresh_token", refresh, httponly=True, path="/v1/auth/refresh")
    return {"status": "ok"}


@v1_router.post("/logout")
async def logout(
    service: Annotated[AuthService, Depends(ServiceFactory.auth_service_factory)],
    refresh_token_data: RefreshTokenDep,
    response: Response,
):
    try:
        await service.delete_refresh_token(refresh_token_data)
    except InvalidRefreshTokenException:
        raise InvalidRefreshTokenHTTPException
    except RefreshTokenNotFoundException:
        raise NoRefreshTokenHTTPException
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"status": "ok"}
