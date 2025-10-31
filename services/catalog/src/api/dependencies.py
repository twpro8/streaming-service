from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request, Query
from fastapi.openapi.models import Example
from pydantic import BaseModel

from src.enums import SortBy, SortOrder
from src.exceptions import (
    NoAccessTokenException,
    PermissionDeniedException,
    UnknownSortFieldException,
    UnknownSortOrderException,
)
from src.services.auth import AuthService


def get_token(request: Request) -> str:
    token = request.cookies.get("access_token", None)
    if not token:
        raise NoAccessTokenException
    return token


def get_current_user_id(token: str = Depends(get_token)) -> UUID:
    data = AuthService().decode_token(token)
    return data["user_id"]


UserIDDep = Annotated[UUID, Depends(get_current_user_id)]


def get_admin(token: str = Depends(get_token)):
    data = AuthService().decode_token(token)
    is_admin = data.get("is_admin", False)

    if isinstance(is_admin, str):
        is_admin = is_admin.lower() == "true"

    if not is_admin:
        raise PermissionDeniedException


AdminDep = Depends(get_admin)


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(default=1, ge=1)]
    per_page: Annotated[int | None, Query(default=5, ge=1, le=100)]


PaginationDep = Annotated[PaginationParams, Depends()]


class SortParams(BaseModel):
    field: SortBy | None = None
    order: SortOrder | None = None

    @classmethod
    def from_query(
        cls,
        sort: str | None = Query(
            None,
            description="""
            Sort items by their specific field. 
            Use "asc" for ascending or "desc" for descending. 
            Default is "desc" if not specified.
            """,
            openapi_examples={
                "1": Example(
                    summary="Sort by ID ascending",
                    value="id:asc",
                ),
                "2": Example(
                    summary="Sort by ID descending",
                    value="id:desc",
                ),
                "3": Example(
                    summary="Sort by title ascending",
                    value="title:asc",
                ),
                "4": Example(
                    summary="Sort by title descending",
                    value="title:desc",
                ),
                "5": Example(
                    summary="Sort by year ascending",
                    value="year:asc",
                ),
                "6": Example(
                    summary="Sort by year descending",
                    value="year:desc",
                ),
                "7": Example(
                    summary="Sort by rating ascending",
                    value="rating:asc",
                ),
                "8": Example(
                    summary="Sort by rating descending",
                    value="rating:desc",
                ),
                "9": Example(
                    summary="Sort by creation date ascending",
                    value="created_at:asc",
                ),
                "10": Example(
                    summary="Sort by creation date descending",
                    value="created_at:desc",
                ),
                "11": Example(
                    summary="Sort by update date ascending",
                    value="updated_at:asc",
                ),
                "12": Example(
                    summary="Sort by update date descending",
                    value="updated_at:desc",
                ),
            },
        ),
    ):
        if not sort:
            return cls()

        parts = sort.split(":")

        field = parts[0].lower()
        if field not in SortBy.__members__:
            raise UnknownSortFieldException(detail=f"Unknown sort field: {field}")

        order = parts[1].lower() if len(parts) > 1 else "desc"
        if order not in SortOrder.__members__:
            raise UnknownSortOrderException(detail=f"Unknown sort order: {order}")

        return cls(field=SortBy(field), order=SortOrder(order))


SortDep = Annotated[SortParams, Depends(SortParams.from_query)]


class CommonContentParams(PaginationParams):
    title: Annotated[str | None, Query(None, min_length=3, max_length=256)]
    year: Annotated[int | None, Query(None)]
    year_gt: Annotated[int | None, Query(None)]
    year_lt: Annotated[int | None, Query(None)]
    rating: Annotated[Decimal | None, Query(None, ge=0, le=10)]
    rating_gt: Annotated[Decimal | None, Query(None, ge=0, le=10)]
    rating_lt: Annotated[Decimal | None, Query(None, ge=0, le=10)]


ContentParamsDep = Annotated[CommonContentParams, Depends()]
