from typing import List

from fastapi import APIRouter, Query

from src.schemas.series import SeriesAddRequestDTO
from src.services.series import SeriesService
from src.views.dependencies import DBDep, AdminDep


router = APIRouter(prefix="/series", tags=["Series"])


@router.get("")
async def get_series(db: DBDep, ids: List[int | None] = Query()):
    series = await SeriesService(db).get_series(ids)
    return {"status": "ok", "data": series}


@router.post("", dependencies=[AdminDep])
async def add_new_series(db: DBDep, data: SeriesAddRequestDTO):
    series = await SeriesService(db).add_series(data)
    return {"status": "ok", "data": series}


@router.patch("", dependencies=[AdminDep])
async def partly_update_series(db: DBDep):
    ...


@router.delete("", dependencies=[AdminDep])
async def delete_series(db: DBDep):
    ...
