from uuid import UUID

from fastapi import APIRouter, Query

from src.exceptions import (
    SeasonNotFoundException,
    SeriesNotFoundException,
    SeriesNotFoundHTTPException,
    SeasonNotFoundHTTPException,
    UniqueSeasonNumberException,
    UniqueSeasonNumberHTTPException,
    UniqueSeasonPerSeriesException,
    UniqueSeasonPerSeriesHTTPException,
)
from src.schemas.seasons import SeasonAddDTO, SeasonPatchRequestDTO
from src.services.seasons import SeasonService
from src.api.dependencies import DBDep, AdminDep, PaginationDep


router = APIRouter(prefix="/seasons", tags=["Seasons"])


@router.get("")
async def get_seasons(db: DBDep, pagination: PaginationDep, series_id: UUID = Query()):
    data = await SeasonService(db).get_seasons(
        series_id=series_id,
        page=pagination.page,
        per_page=pagination.per_page,
    )
    return {"status": "ok", "data": data}


@router.get("/{season_id}")
async def get_season(db: DBDep, season_id: UUID):
    try:
        data = await SeasonService(db).get_season(season_id=season_id)
    except SeasonNotFoundException:
        raise SeasonNotFoundHTTPException
    return {"status": "ok", "data": data}


@router.post("", dependencies=[AdminDep], status_code=201)
async def add_season(db: DBDep, season_data: SeasonAddDTO):
    try:
        data = await SeasonService(db).add_season(season_data=season_data)
    except SeriesNotFoundException:
        raise SeriesNotFoundHTTPException
    except UniqueSeasonPerSeriesException:
        raise UniqueSeasonPerSeriesHTTPException
    return {"status": "ok", "data": data}


@router.patch("/{season_id}", dependencies=[AdminDep])
async def update_season(db: DBDep, season_id: UUID, season_data: SeasonPatchRequestDTO):
    try:
        await SeasonService(db).update_season(season_id=season_id, season_data=season_data)
    except SeasonNotFoundException:
        raise SeasonNotFoundHTTPException
    except UniqueSeasonNumberException:
        raise UniqueSeasonNumberHTTPException
    return {"status": "ok"}


@router.delete("/{season_id}", dependencies=[AdminDep], status_code=204)
async def delete_season(db: DBDep, season_id: UUID):
    await SeasonService(db).delete_season(season_id=season_id)
