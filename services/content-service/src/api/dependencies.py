from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request, Query
from fastapi.openapi.models import Example
from pydantic import BaseModel

from src.db import DBManager, session_maker
from src.enums import SortBy, SortOrder
from src.exceptions import (
    NoTokenHTTPException,
    PermissionDeniedHTTPException,
    UnknownSortFieldHTTPException,
    UnknownSortOrderHTTPException,
)
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


class SortParams(BaseModel):
    field: SortBy | None = None
    order: SortOrder | None = None

    @classmethod
    def from_query(
        cls,
        sort: str | None = Query(
            None,
            openapi_examples={
                "sort_id_asc": Example(
                    summary="Sort by ID ascending",
                    description='Sort items by their ID. Use "asc" for ascending or "desc" for descending. Default is "asc" if not specified.',
                    value="id:asc",
                ),
                "sort_id_desc": Example(
                    summary="Sort by ID descending",
                    description='Sort items by their ID. Use "asc" for ascending or "desc" for descending. Default is "asc" if not specified.',
                    value="id:desc",
                ),
                "sort_title_asc": Example(
                    summary="Sort by title ascending",
                    description='Sort items alphabetically by title. Use "asc" for A→Z or "desc" for Z→A. Default is "asc" if not specified.',
                    value="title:asc",
                ),
                "sort_title_desc": Example(
                    summary="Sort by title descending",
                    description='Sort items alphabetically by title. Use "asc" for A→Z or "desc" for Z→A. Default is "asc" if not specified.',
                    value="title:desc",
                ),
                "sort_year_asc": Example(
                    summary="Sort by year ascending",
                    description='Sort items by their release year. Use "asc" for oldest to newest or "desc" for newest to oldest. Default is "asc" if not specified.',
                    value="release_year:asc",
                ),
                "sort_year_desc": Example(
                    summary="Sort by year descending",
                    description='Sort items by their release year. Use "asc" for oldest to newest or "desc" for newest to oldest. Default is "asc" if not specified.',
                    value="year:desc",
                ),
                "sort_rating_asc": Example(
                    summary="Sort by rating ascending",
                    description='Sort items by rating score. Use "asc" for lowest to highest or "desc" for highest to lowest. Default is "asc" if not specified.',
                    value="rating:asc",
                ),
                "sort_rating_desc": Example(
                    summary="Sort by rating descending",
                    description='Sort items by rating score. Use "asc" for lowest to highest or "desc" for highest to lowest. Default is "asc" if not specified.',
                    value="rating:desc",
                ),
            },
        ),
    ):
        if not sort:
            return cls()

        parts = sort.split(":")

        field = parts[0].lower()
        if field not in SortBy.__members__:
            raise UnknownSortFieldHTTPException(detail=f"Unknown sort field: {field}")

        order = parts[1].lower() if len(parts) > 1 else "asc"
        if order not in SortOrder.__members__:
            raise UnknownSortOrderHTTPException(detail=f"Unknown sort order: {order}")

        return cls(field=SortBy(field), order=SortOrder(order))


SortDep = Annotated[SortParams, Depends(SortParams.from_query)]


class CommonContentParams(PaginationParams):
    title: Annotated[str | None, Query(None)]
    description: Annotated[str | None, Query(None)]
    director: Annotated[str | None, Query(None)]
    year: Annotated[int | None, Query(None)]
    year_gt: Annotated[int | None, Query(None)]
    year_lt: Annotated[int | None, Query(None)]
    rating: Annotated[Decimal | None, Query(None, ge=0, le=10)]
    rating_ge: Annotated[Decimal | None, Query(None, ge=0, le=10)]
    rating_le: Annotated[Decimal | None, Query(None, ge=0, le=10)]


ContentParamsDep = Annotated[CommonContentParams, Depends()]


class EpisodesParams(PaginationParams):
    title: Annotated[str | None, Query(None)]
    series_id: Annotated[UUID | None, Query(None)]
    season_id: Annotated[UUID | None, Query(None)]
    episode_number: Annotated[int | None, Query(None, ge=1, le=9999)]


EpisodesParamsDep = Annotated[EpisodesParams, Depends()]
