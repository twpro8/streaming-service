from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from src.exceptions import (
    SeriesNotFoundException,
    SeriesNotFoundHTTPException,
    UniqueCoverURLException,
    UniqueCoverURLHTTPException,
    GenreNotFoundException,
    GenreNotFoundHTTPException,
)
from src.schemas.series import SeriesAddRequestDTO, SeriesPatchRequestDTO
from src.services.series import SeriesService
from src.api.dependencies import DBDep, AdminDep, ContentParamsDep


router = APIRouter(prefix="/series", tags=["Series"])


@router.get("")
async def get_series(
    db: DBDep,
    common_params: ContentParamsDep,
    genres: Annotated[list[int] | None, Query()] = None,
):
    series = await SeriesService(db).get_series(**common_params.model_dump(), genres=genres)
    return {"status": "ok", "data": series}


@router.get("/{series_id}")
async def get_one_series(db: DBDep, series_id: UUID):
    try:
        series = await SeriesService(db).get_one_series(series_id)
    except SeriesNotFoundException:
        raise SeriesNotFoundHTTPException
    return {"status": "ok", "data": series}


@router.post("", dependencies=[AdminDep], status_code=201)
async def add_series(db: DBDep, series_data: SeriesAddRequestDTO):
    try:
        series = await SeriesService(db).add_series(series_data)
    except UniqueCoverURLException:
        raise UniqueCoverURLHTTPException
    except GenreNotFoundException:
        raise GenreNotFoundHTTPException
    return {"status": "ok", "data": series}


@router.patch("/{series_id}", dependencies=[AdminDep])
async def update_series(db: DBDep, series_id: UUID, series_data: SeriesPatchRequestDTO):
    try:
        await SeriesService(db).update_series(series_id, series_data)
    except SeriesNotFoundException:
        raise SeriesNotFoundHTTPException
    except UniqueCoverURLException:
        raise UniqueCoverURLHTTPException
    except GenreNotFoundException:
        raise GenreNotFoundHTTPException
    return {"status": "ok"}


@router.delete("/{series_id}", dependencies=[AdminDep], status_code=204)
async def delete_series(db: DBDep, series_id: UUID):
    await SeriesService(db).delete_series(series_id)
