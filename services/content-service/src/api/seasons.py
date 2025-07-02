from uuid import UUID

from fastapi import APIRouter

from src.exceptions import (
    SeasonNotFoundException,
    SeasonAlreadyExistsException,
    SeriesNotFoundException,
    SeriesNotFoundHTTPException,
    SeasonAlreadyExistsHTTPException,
    SeasonNotFoundHTTPException,
)
from src.schemas.seasons import SeasonAddRequestDTO, SeasonPatchRequestDTO
from src.services.seasons import SeasonService
from src.api.dependencies import DBDep, AdminDep, PaginationDep


router = APIRouter(prefix="/series", tags=["Seasons"])


@router.get("/{series_id}/seasons")
async def get_seasons(db: DBDep, series_id: UUID, pagination: PaginationDep):
    data = await SeasonService(db).get_seasons(series_id=series_id, pagination=pagination)
    return {"status": "ok", "data": data}


@router.post("/{series_id}/seasons", dependencies=[AdminDep])
async def add_season(db: DBDep, series_id: UUID, season_data: SeasonAddRequestDTO):
    try:
        data = await SeasonService(db).add_season(series_id=series_id, season_data=season_data)
    except SeriesNotFoundException:
        raise SeriesNotFoundHTTPException
    except SeasonAlreadyExistsException:
        raise SeasonAlreadyExistsHTTPException
    return {"status": "ok", "data": data}


@router.patch("/{series_id}/seasons/{season_id}", dependencies=[AdminDep])
async def update_season(
    db: DBDep, series_id: UUID, season_id: UUID, season_data: SeasonPatchRequestDTO
):
    try:
        await SeasonService(db).update_season(
            series_id=series_id,
            season_id=season_id,
            season_data=season_data,
        )
    except SeriesNotFoundException:
        raise SeriesNotFoundHTTPException
    except SeasonNotFoundException:
        raise SeasonNotFoundHTTPException
    return {"status": "ok"}


@router.delete("/{series_id}/seasons/{season_id}", dependencies=[AdminDep], status_code=204)
async def delete_season(db: DBDep, series_id: UUID, season_id: UUID):
    await SeasonService(db).delete_season(series_id=series_id, season_id=season_id)
