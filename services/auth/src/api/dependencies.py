from pydantic import BaseModel
from typing import Annotated

from fastapi import Depends, Request, HTTPException, Query

from src.db import session_maker
from src.managers.db import DBManager
from src.services.auth import AuthService


def get_db_manager():
    return DBManager(session_factory=session_maker)


async def get_db():
    async with get_db_manager() as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]


def get_token(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No token")
    return token


def get_current_user_id(token: str = Depends(get_token)):
    data = AuthService().decode_token(token)
    return data.get("user_id")


UserIDDep = Annotated[int, Depends(get_current_user_id)]


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(default=1, ge=1)]
    per_page: Annotated[int | None, Query(default=5, ge=1, le=100)]


PaginationDep = Annotated[PaginationParams, Depends()]
