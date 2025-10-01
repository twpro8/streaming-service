from uuid import UUID

from pydantic import BaseModel
from typing import Annotated

from fastapi import Depends, Request, HTTPException, Query

from src.factories.db_manager import DBManagerFactory
from src.managers.db import DBManager
from src.managers.redis import RedisManager
from src.adapters.aiohttp import HTTPClient
from src.services.auth import AuthService
from src import redis_manager, aiohttp_client


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


def get_async_http_client() -> HTTPClient:
    return aiohttp_client


DBDep = Annotated[DBManager, Depends(get_db)]
UserIDDep = Annotated[UUID, Depends(get_current_user_id)]
PaginationDep = Annotated[PaginationParams, Depends()]
RedisManagerDep = Annotated[RedisManager, Depends(get_redis_manager)]
HTTPClientDep = Annotated[HTTPClient, Depends(get_async_http_client)]
