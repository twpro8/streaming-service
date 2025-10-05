from uuid import UUID

from pydantic import BaseModel
from typing import Annotated

from fastapi import Depends, Request, HTTPException, Query

from src.factories.db_manager import DBManagerFactory
from src.managers.db import DBManager
from src.managers.redis import RedisManager
from src.adapters.aiohttp_client import AiohttpClient
from src.services.auth import AuthService
from src import (
    redis_manager,
    aiohttp_client,
    GoogleOAuthClient,
    google_oauth_client,
    jwt_provider,
    password_hasher,
    JwtProvider,
    PasswordHasher,
)


async def get_db():
    async with DBManagerFactory.create() as db:
        yield db


def get_token(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No token")
    return token


def get_current_user_id(token: str = Depends(get_token)):
    data = AuthService.decode_token(token)
    return data.get("user_id")


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(default=1, ge=1)]
    per_page: Annotated[int | None, Query(default=5, ge=1, le=100)]


def get_redis_manager() -> RedisManager:
    return redis_manager


def get_async_http_client() -> AiohttpClient:
    return aiohttp_client


def get_google_oauth_client() -> GoogleOAuthClient:
    return google_oauth_client


def get_jwt_provider() -> JwtProvider:
    return jwt_provider


def get_password_hasher() -> PasswordHasher:
    return password_hasher


DBDep = Annotated[DBManager, Depends(get_db)]
UserIDDep = Annotated[UUID, Depends(get_current_user_id)]
PaginationDep = Annotated[PaginationParams, Depends()]
RedisManagerDep = Annotated[RedisManager, Depends(get_redis_manager)]
HTTPClientDep = Annotated[AiohttpClient, Depends(get_async_http_client)]
GoogleOAuthClientDep = Annotated[GoogleOAuthClient, Depends(get_google_oauth_client)]
JwtProviderDep = Annotated[JwtProvider, Depends(get_jwt_provider)]
PasswordHasherDep = Annotated[PasswordHasher, Depends(get_password_hasher)]
