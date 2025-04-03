from typing import Annotated

from fastapi import Depends, Request

from src.db import DBManager, session_maker
from src.exceptions import NoTokenHTTPException
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

UserIdDep = Annotated[int, Depends(get_current_user_id)]


def get_admin_rights(token: str = Depends(get_token)):
    data = AuthService().decode_token(token)
    return data.get("is_admin", None)

AdminDep = Annotated[UserIdDep, Depends(get_admin_rights)]
