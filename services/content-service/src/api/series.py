from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Query

from src.exceptions import SeriesNotFoundException, SeriesNotFoundHTTPException
from src.schemas.series import (
    SeriesAddRequestDTO,
    SeriesPatchRequestDTO,
    SeriesPutRequestDTO,
)
from src.services.series import SeriesService
from src.api.dependencies import DBDep, AdminDep, PaginationDep

router = APIRouter(prefix="/series", tags=["Series"])


@router.get("")
async def get_series(
    db: DBDep,
    pagination: PaginationDep,
    title: str | None = Query(None),
    description: str | None = Query(None),
    director: str | None = Query(None),
    release_year: date | None = Query(None),
    release_year_ge: date | None = Query(None),
    release_year_le: date | None = Query(None),
    rating: Decimal | None = Query(None, ge=0, le=10),
    rating_ge: Decimal | None = Query(None, ge=0, le=10),
    rating_le: Decimal | None = Query(None, ge=0, le=10),
):
    series = await SeriesService(db).get_series(
        page=pagination.page,
        per_page=pagination.per_page,
        title=title,
        description=description,
        director=director,
        release_year=release_year,
        release_year_ge=release_year_ge,
        release_year_le=release_year_le,
        rating=rating,
        rating_ge=rating_ge,
        rating_le=rating_le,
    )
    return {"status": "ok", "data": series}


@router.get("/{series_id}")
async def get_one_series(db: DBDep, series_id: UUID):
    try:
        series = await SeriesService(db).get_one_series(series_id)
    except SeriesNotFoundException:
        raise SeriesNotFoundHTTPException
    return {"status": "ok", "data": series}


@router.post("", dependencies=[AdminDep])
async def add_new_series(db: DBDep, data: SeriesAddRequestDTO):
    series = await SeriesService(db).add_series(data)
    return {"status": "ok", "data": series}


@router.put("/{series_id}", dependencies=[AdminDep])
async def replace_series(db: DBDep, series_id: UUID, series_data: SeriesPutRequestDTO):
    try:
        await SeriesService(db).replace_series(series_id, series_data)
    except SeriesNotFoundException:
        raise SeriesNotFoundHTTPException
    return {"status": "ok"}


@router.patch("/{series_id}", dependencies=[AdminDep])
async def update_series(db: DBDep, series_id: UUID, series_data: SeriesPatchRequestDTO):
    try:
        await SeriesService(db).update_series(series_id, series_data)
    except SeriesNotFoundException:
        raise SeriesNotFoundHTTPException
    return {"status": "ok"}


@router.delete("/{series_id}", dependencies=[AdminDep], status_code=204)
async def delete_series(db: DBDep, series_id: UUID):
    await SeriesService(db).delete_series(series_id)
