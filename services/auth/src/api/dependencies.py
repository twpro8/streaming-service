from uuid import UUID

from pydantic import BaseModel
from typing import Annotated

from fastapi import Depends, Request, Query, Cookie

from src.exceptions import (
    JWTProviderException,
    InvalidRefreshTokenHTTPException,
    NoRefreshTokenHTTPException,
    NoAccessTokenHTTPException,
    InvalidAccessTokenHTTPException,
    UserAlreadyAuthorizedHTTPException,
)
from src.factories.db_manager import DBManagerFactory
from src.adapters.aiohttp_client import AiohttpClient
from src.adapters.google_client import GoogleOAuthClient
from src.adapters.jwt_provider import JwtProvider
from src.adapters.password_hasher import PasswordHasher
from src.managers.db import DBManager
from src.managers.redis import RedisManager
from src import (
    redis_manager,
    aiohttp_client,
    google_oauth_client,
    jwt_provider,
    password_hasher,
)
from src.schemas.auth import ClientInfo


async def get_db():
    async with DBManagerFactory.create() as db:
        yield db


def get_access_token(access_token: Annotated[str | None, Cookie()] = None) -> str:
    if not access_token:
        raise NoAccessTokenHTTPException

    return access_token


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(default=1, ge=1)]
    per_page: Annotated[int | None, Query(default=5, ge=1, le=100)]


def get_redis_manager() -> RedisManager:
    return redis_manager


def get_async_http_client() -> AiohttpClient:
    return aiohttp_client


def get_google_oauth_client() -> GoogleOAuthClient:
    return google_oauth_client


def get_password_hasher() -> PasswordHasher:
    return password_hasher


def get_jwt_provider() -> JwtProvider:
    return jwt_provider


def get_current_user_id(
    jwt: Annotated[JwtProvider, Depends(get_jwt_provider)],
    token: Annotated[str, Depends(get_access_token)],
) -> UUID:
    try:
        data = jwt.decode_token(token)
    except JWTProviderException:
        raise InvalidAccessTokenHTTPException

    return data.get("id")


def get_client_info(request: Request) -> ClientInfo:
    ip = request.headers.get("x-forwarded-for") or request.client.host
    user_agent = request.headers.get("user-agent", "unknown")

    return ClientInfo(ip=ip, user_agent=user_agent)


def get_refresh_token(
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> str:
    if not refresh_token:
        raise NoRefreshTokenHTTPException

    return refresh_token


def get_refresh_token_data(
    refresh_token: Annotated[str, Depends(get_refresh_token)],
    jwt: Annotated[JwtProvider, Depends(get_jwt_provider)] = None,
) -> dict:
    try:
        payload = jwt.decode_token(refresh_token)
    except JWTProviderException:
        raise InvalidRefreshTokenHTTPException

    return payload


def prevent_duplicate_login(
    access_token: Annotated[str | None, Cookie()] = None,
    jwt: Annotated[JwtProvider, Depends(get_jwt_provider)] = None,
):
    if not access_token:
        return None

    try:
        jwt.decode_token(access_token)
    except JWTProviderException:
        # token is invalid or expired, a new one can be issued
        return None

    # token is valid, user is already authorized
    raise UserAlreadyAuthorizedHTTPException


DBDep = Annotated[DBManager, Depends(get_db)]
UserIDDep = Annotated[UUID, Depends(get_current_user_id)]
PaginationDep = Annotated[PaginationParams, Depends()]
RedisManagerDep = Annotated[RedisManager, Depends(get_redis_manager)]
HTTPClientDep = Annotated[AiohttpClient, Depends(get_async_http_client)]
GoogleOAuthClientDep = Annotated[GoogleOAuthClient, Depends(get_google_oauth_client)]
JwtProviderDep = Annotated[JwtProvider, Depends(get_jwt_provider)]
PasswordHasherDep = Annotated[PasswordHasher, Depends(get_password_hasher)]
ClientInfoDep = Annotated[ClientInfo, Depends(get_client_info)]
RefreshTokenDep = Annotated[dict, Depends(get_refresh_token_data)]
PreventDuplicateLoginDep = Depends(prevent_duplicate_login)
