from fastapi import APIRouter

from src.schemas.series import SeriesAddRequestDTO
from src.services.series import SeriesService
from src.views.dependencies import DBDep, AdminDep


router = APIRouter(prefix="/series", tags=["Series"])


@router.get("")
async def get_series(db: DBDep):
    ...


@router.get("/{series_id}")
async def get_one_series(db: DBDep):
    ...


@router.post("", dependencies=[AdminDep])
async def add_new_series(db: DBDep, data: SeriesAddRequestDTO):
    series = await SeriesService(db).add_series(data)
    return {"status": "success", "series": series}


@router.patch("", dependencies=[AdminDep])
async def partly_update_series(db: DBDep):
    ...


@router.delete("", dependencies=[AdminDep])
async def delete_series(db: DBDep):
    ...
