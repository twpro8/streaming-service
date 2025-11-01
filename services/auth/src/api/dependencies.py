from uuid import UUID
from functools import lru_cache

from pydantic import BaseModel
from typing import Annotated

from fastapi import Depends, Request, Query, Cookie, Body

from src.config import settings
from src.exceptions import (
    JWTProviderException,
    InvalidRefreshTokenException,
    NoRefreshTokenException,
    NoAccessTokenException,
    InvalidTokenException,
    AlreadyAuthorizedException,
    TooManyRequestsException,
)
from src.factories.db_manager import DBManagerFactory
from src.adapters.aiohttp_client import AiohttpClient
from src.adapters.google_client import GoogleOAuthClient
from src.adapters.jwt_provider import JwtProvider
from src.adapters.password_hasher import PasswordHasher
from src.managers.db import DBManager
from src.managers.redis import RedisManager
from src.schemas.auth import ClientInfo
from src.schemas.pydatic_types import EmailStr


async def get_db():
    async with DBManagerFactory.create() as db:
        yield db


def get_access_token(access_token: Annotated[str | None, Cookie()] = None) -> str:
    if not access_token:
        raise NoAccessTokenException

    return access_token


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(default=1, ge=1)]
    per_page: Annotated[int | None, Query(default=5, ge=1, le=100)]


@lru_cache
def get_redis_manager() -> RedisManager:
    return RedisManager(url=settings.REDIS_URL)


@lru_cache
def get_async_http_client() -> AiohttpClient:
    return AiohttpClient()


@lru_cache
def get_google_oauth_client(
    aiohttp_client: Annotated[AiohttpClient, Depends(get_async_http_client)],
    redis_manager: Annotated[RedisManager, Depends(get_redis_manager)],
) -> GoogleOAuthClient:
    return GoogleOAuthClient(
        ac=aiohttp_client,
        redis=redis_manager,
        client_id=settings.OAUTH_GOOGLE_CLIENT_ID,
        client_secret=settings.OAUTH_GOOGLE_CLIENT_SECRET,
        base_url=settings.OAUTH_GOOGLE_BASE_URL,
        redirect_uri=settings.OAUTH_GOOGLE_REDIRECT_URL,
        token_url=settings.GOOGLE_TOKEN_URL,
        jwks_url=settings.GOOGLE_JWKS_URL,
    )


@lru_cache
def get_password_hasher() -> PasswordHasher:
    return PasswordHasher(schemes=["bcrypt"], deprecated="auto")


@lru_cache
def get_jwt_provider() -> JwtProvider:
    return JwtProvider(
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        access_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_expire_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )


def get_current_user_id(
    jwt: Annotated[JwtProvider, Depends(get_jwt_provider)],
    token: Annotated[str, Depends(get_access_token)],
) -> UUID:
    try:
        data = jwt.decode_token(token)
    except JWTProviderException:
        raise InvalidTokenException

    return data.get("id")


def get_client_info(request: Request) -> ClientInfo:
    ip = request.headers.get("x-forwarded-for") or request.client.host
    user_agent = request.headers.get("user-agent", "unknown")

    return ClientInfo(ip=ip, user_agent=user_agent)


def get_refresh_token(
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> str:
    if not refresh_token:
        raise NoRefreshTokenException

    return refresh_token


def get_refresh_token_data(
    refresh_token: Annotated[str, Depends(get_refresh_token)],
    jwt: Annotated[JwtProvider, Depends(get_jwt_provider)] = None,
) -> dict:
    try:
        payload = jwt.decode_token(refresh_token)
    except JWTProviderException:
        raise InvalidRefreshTokenException

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
    raise AlreadyAuthorizedException


async def get_email_rate_limiter(
    redis: Annotated[RedisManager, Depends(get_redis_manager)],
    email: EmailStr = Body(embed=True),
):
    # checking rate limit
    rate_limit_key = f"rate-limit:{email}"
    if await redis.get(rate_limit_key):
        raise TooManyRequestsException

    # setting rate limit
    await redis.set(rate_limit_key, "1", expire=settings.USER_VERIFY_RATE_LIMIT)


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
