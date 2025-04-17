from typing import List

from fastapi import APIRouter, Query

from src.exceptions import SeriesNotFoundHTTPException
from src.schemas.series import (
    SeriesAddRequestDTO,
    SeriesPatchRequestDTO,
    SeriesPutRequestDTO,
)
from src.services.series import SeriesService
from src.views.dependencies import DBDep, AdminDep


router = APIRouter(prefix="/series", tags=["Series"])


@router.get("")
async def get_series(db: DBDep, ids: List[int | None] = Query(None)):
    series = await SeriesService(db).get_series(ids)
    return {"status": "ok", "data": series}


@router.post("", dependencies=[AdminDep])
async def add_new_series(db: DBDep, data: SeriesAddRequestDTO):
    series = await SeriesService(db).add_series(data)
    return {"status": "ok", "data": series}


@router.put("/{series_id}", dependencies=[AdminDep])
async def update_entire_series(db: DBDep, series_id: int, series_data: SeriesPutRequestDTO):
    await SeriesService(db).update_entire_series(series_id, series_data)
    return {"status": "ok"}


@router.patch("/{series_id}", dependencies=[AdminDep])
async def partly_update_series(db: DBDep, series_id: int, series_data: SeriesPatchRequestDTO):
    await SeriesService(db).partly_update_series(series_id, series_data)
    return {"status": "ok"}


@router.delete("/{series_id}", dependencies=[AdminDep])
async def delete_series(db: DBDep, series_id: int):
    await SeriesService(db).delete_series(series_id)
    return {"status": "ok"}
