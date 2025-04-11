from fastapi import APIRouter

from src.schemas.seasons import SeasonAddRequestDTO, SeasonPatchRequestDTO
from src.services.seasons import SeasonService
from src.views.dependencies import DBDep, AdminDep


router = APIRouter(prefix="/series", tags=["Seasons"])


@router.get("/{series_id}/seasons")
async def get_seasons(db: DBDep, series_id: int):
    data = await SeasonService(db).get_seasons(series_id=series_id)
    return {"status": "ok", "data": data}


@router.post("/{series_id}/seasons", dependencies=[AdminDep])
async def add_season(db: DBDep, series_id: int, season_data: SeasonAddRequestDTO):
    data = await SeasonService(db).add_season(series_id=series_id, season_data=season_data)
    return {"status": "ok", "data": data}


@router.patch("/{series_id}/seasons/{season_id}", dependencies=[AdminDep])
async def update_season(
    db: DBDep, series_id: int, season_id: int, season_data: SeasonPatchRequestDTO
):
    await SeasonService(db).update_season(
        series_id=series_id,
        season_id=season_id,
        season_data=season_data,
    )
    return {"status": "ok"}


@router.delete("/{series_id}/seasons/{season_id}", dependencies=[AdminDep])
async def delete_season(db: DBDep, series_id: int, season_id: int):
    await SeasonService(db).delete_season(series_id=series_id, season_id=season_id)
    return {"status": "ok"}
