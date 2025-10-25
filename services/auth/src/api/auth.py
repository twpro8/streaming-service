from typing import Annotated

from fastapi import APIRouter, Body
from fastapi.responses import Response
from fastapi import Depends

from src.api.dependencies import (
    ClientInfoDep,
    RefreshTokenDep,
    PreventDuplicateLoginDep,
    UserIDDep,
    get_email_rate_limiter,
)
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
    InvalidVerificationCodeException,
    InvalidVerificationCodeHTTPException,
    UserAlreadyVerifiedException,
    UserAlreadyVerifiedHTTPException,
    TooManyRequestsException,
    TooManyRequestsHTTPException,
    SamePasswordException,
    SamePasswordHTTPException,
    UserUnverifiedException,
    UserUnverifiedHTTPException,
)
from src.factories.service import ServiceFactory
from src.schemas.auth import (
    EmailVerifyRequestDTO,
    PasswordChangeRequestDTO,
    PasswordResetRequestDTO,
)
from src.schemas.pydatic_types import EmailStr
from src.schemas.users import UserAddRequestDTO, UserLoginRequestDTO
from src.services.auth import AuthService


v1_router = APIRouter(prefix="/v1/auth", tags=["Auth"])


@v1_router.post("/login", dependencies=[PreventDuplicateLoginDep])
async def login(
    service: Annotated[AuthService, Depends(ServiceFactory.auth_service_factory)],
    user_data: UserLoginRequestDTO,
    client_info: ClientInfoDep,
    response: Response,
):
    try:
        access, refresh = await service.login(user_data, client_info)
    except UserNotFoundException:
        raise UserNotFoundHTTPException
    except IncorrectPasswordException:
        raise IncorrectPasswordHTTPException
    except UserUnverifiedException:
        raise UserUnverifiedHTTPException
    response.set_cookie("access_token", access, httponly=True)
    response.set_cookie("refresh_token", refresh, httponly=True)
    return {"status": "ok"}


@v1_router.post("/signup", status_code=201)
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


@v1_router.post("/verify-email")
async def verify_email(
    service: Annotated[AuthService, Depends(ServiceFactory.auth_service_factory)],
    form_data: EmailVerifyRequestDTO,
):
    try:
        await service.verify_email(form_data)
    except InvalidVerificationCodeException:
        raise InvalidVerificationCodeHTTPException
    except UserNotFoundException:
        raise UserNotFoundHTTPException
    return {"status": "verified"}


@v1_router.post("/resend-code", dependencies=[Depends(get_email_rate_limiter)])
async def resend_verification_code(
    service: Annotated[AuthService, Depends(ServiceFactory.auth_service_factory)],
    email: EmailStr = Body(embed=True),
):
    try:
        await service.resend_verification_code(email)
    except UserNotFoundException:
        raise UserNotFoundHTTPException
    except UserAlreadyVerifiedException:
        raise UserAlreadyVerifiedHTTPException
    except TooManyRequestsException:
        raise TooManyRequestsHTTPException
    return {"status": "ok"}


@v1_router.post("/forgot-password", dependencies=[Depends(get_email_rate_limiter)])
async def forgot_password(
    service: Annotated[AuthService, Depends(ServiceFactory.auth_service_factory)],
    email: EmailStr = Body(embed=True),
):
    try:
        await service.forgot_password(email)
    except TooManyRequestsException:
        raise TooManyRequestsHTTPException
    except UserNotFoundException:
        raise UserNotFoundHTTPException
    return {"status": "ok"}


@v1_router.post("/reset-password-confirmation")
async def reset_password_confirmation(
    service: Annotated[AuthService, Depends(ServiceFactory.auth_service_factory)],
    form_data: PasswordResetRequestDTO,
):
    try:
        await service.reset_password(form_data)
    except InvalidVerificationCodeException:
        raise InvalidVerificationCodeHTTPException
    return {"status": "ok"}


@v1_router.post("/change-password")
async def change_password(
    service: Annotated[AuthService, Depends(ServiceFactory.auth_service_factory)],
    user_id: UserIDDep,
    form_data: PasswordChangeRequestDTO,
):
    try:
        await service.change_password(user_id, form_data)
    except IncorrectPasswordException:
        raise IncorrectPasswordHTTPException
    except SamePasswordException:
        raise SamePasswordHTTPException
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
