from typing import Annotated

from fastapi import APIRouter
from fastapi.responses import Response
from fastapi.params import Depends

from src.api.dependencies import ClientInfoDep, RefreshTokenDep, PreventDuplicateLoginDep
from src.exceptions import (
    UserNotFoundException,
    UserNotFoundHTTPException,
    InvalidRefreshTokenException,
    InvalidRefreshTokenHTTPException,
    RefreshTokenNotFoundException,
    NoRefreshTokenHTTPException,
    IncorrectPasswordException,
    IncorrectPasswordHTTPException,
    UserAlreadyExistsException,
    UserAlreadyExistsHTTPException,
    TokenRevokedException,
    TokenRevokedHTTPException,
    ClientMismatchException,
    ClientMismatchHTTPException,
    UserAlreadyAuthorizedException,
    UserAlreadyAuthorizedHTTPException,
)
from src.factories.service import ServiceFactory
from src.schemas.users import UserAddRequestDTO, UserLoginDTO
from src.services.auth import AuthService


v1_router = APIRouter(prefix="/v1/auth", tags=["auth"])


@v1_router.post("/login", dependencies=[PreventDuplicateLoginDep])
async def login(
    service: Annotated[AuthService, Depends(ServiceFactory.auth_service_factory)],
    user: UserLoginDTO,
    client_info: ClientInfoDep,
    response: Response,
):
    try:
        access, refresh = await service.login(
            email=user.email,
            password=user.password,
            info=client_info,
        )
    except UserNotFoundException:
        raise UserNotFoundHTTPException
    except IncorrectPasswordException:
        raise IncorrectPasswordHTTPException
    except UserAlreadyAuthorizedException:
        raise UserAlreadyAuthorizedHTTPException
    response.set_cookie("access_token", access, httponly=True)
    response.set_cookie("refresh_token", refresh, httponly=True)
    return {"status": "ok"}


@v1_router.post("/signup")
async def signup(
    service: Annotated[AuthService, Depends(ServiceFactory.auth_service_factory)],
    user_data: UserAddRequestDTO,
):
    try:
        await service.register(user_data)
    except UserAlreadyExistsException:
        raise UserAlreadyExistsHTTPException
    return {"status": "ok"}


@v1_router.post("/refresh")
async def refresh_token(
    service: Annotated[AuthService, Depends(ServiceFactory.auth_service_factory)],
    response: Response,
    client_info: ClientInfoDep,
    refresh_token_data: RefreshTokenDep,
):
    try:
        access, refresh = await service.refresh_token(refresh_token_data, client_info)
    except TokenRevokedException:
        raise TokenRevokedHTTPException
    except UserNotFoundException:
        raise UserNotFoundHTTPException
    except ClientMismatchException:
        raise ClientMismatchHTTPException
    response.set_cookie("access_token", access, httponly=True)
    response.set_cookie("refresh_token", refresh, httponly=True)  # Add path here
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
    response.delete_cookie("refresh_token")  # Add path here
    return {"status": "ok"}
