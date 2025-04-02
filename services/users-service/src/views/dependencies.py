from typing import Annotated

from httpx import AsyncClient
from fastapi import Depends, Request, HTTPException

from src.db import DBManager, session_maker
from src.services.auth import AuthService


def get_db_manager():
    return DBManager(session_factory=session_maker)


async def get_db():
    async with get_db_manager() as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]


def get_token(request: Request) -> str:
    token = request.cookies.get("access_token", None)  # cookie method returns a dict of str cookies
    if not token:
        raise HTTPException(status_code=401, detail="No token")
    return token


def get_current_user_id(token: str = Depends(get_token)):
    data = AuthService().decode_token(token)
    return data.get("user_id", None)


UserIdDep = Annotated[int, Depends(get_current_user_id)]


async def get_async_client():
    async with AsyncClient() as ac:
        yield ac


ACDep = Annotated[AsyncClient, Depends(get_async_client)]
