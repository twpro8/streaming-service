from pydantic import BaseModel
from typing import Annotated

from fastapi import Depends, Request, HTTPException, Query

from src.db import DBManager, session_maker
from src.services.auth import AuthService
from src.grpc.manager import GRPCClientManager


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


class PaginationParams(BaseModel):
    page: Annotated[int, Query(1, ge=1, le=999999)]
    per_page: Annotated[int, Query(5, ge=1, le=30)]


PaginationDep = Annotated[PaginationParams, Depends()]


async def get_grpc_manager():
    async with GRPCClientManager() as grpc_manager:
        yield grpc_manager


gRpcDep = Annotated[GRPCClientManager, Depends(get_grpc_manager)]
