from typing import Annotated

from fastapi import Depends, Request, Query
from pydantic import BaseModel

from src.db import DBManager, session_maker
from src.exceptions import NoTokenHTTPException, PermissionDeniedHTTPException
from src.services.auth import AuthService


def get_db_manager():
    return DBManager(session_factory=session_maker)


async def get_db():
    async with get_db_manager() as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]


def get_token(request: Request) -> str:
    token = request.cookies.get("access_token", None)
    if not token:
        raise NoTokenHTTPException
    return token


def get_current_user_id(token: str = Depends(get_token)):
    data = AuthService().decode_token(token)
    return data.get("user_id", None)


UserDep = Annotated[int, Depends(get_current_user_id)]


def get_admin(token: str = Depends(get_token)):
    data = AuthService().decode_token(token)
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
