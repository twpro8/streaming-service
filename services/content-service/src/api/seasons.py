from uuid import UUID

from fastapi import APIRouter, Query

from src.exceptions import (
    SeasonNotFoundException,
    ShowNotFoundException,
    ShowNotFoundHTTPException,
    SeasonNotFoundHTTPException,
    UniqueSeasonPerShowException,
    SeasonAlreadyExistsHTTPException,
)
from src.schemas.seasons import SeasonPatchRequestDTO, SeasonAddRequestDTO
from src.services.seasons import SeasonService
from src.api.dependencies import DBDep, AdminDep, PaginationDep


v1_router = APIRouter(prefix="/v1/seasons", tags=["seasons"])


@v1_router.get("")
async def get_seasons(db: DBDep, pagination: PaginationDep, show_id: UUID | None = Query(None)):
    data = await SeasonService(db).get_seasons(
        show_id=show_id,
        page=pagination.page,
        per_page=pagination.per_page,
    )
    return {"status": "ok", "data": data}


@v1_router.get("/{season_id}")
async def get_season(db: DBDep, season_id: UUID):
    try:
        data = await SeasonService(db).get_season(season_id=season_id)
    except SeasonNotFoundException:
        raise SeasonNotFoundHTTPException
    return {"status": "ok", "data": data}


@v1_router.post("", dependencies=[AdminDep], status_code=201)
async def add_season(db: DBDep, season_data: SeasonAddRequestDTO):
    try:
        season_id = await SeasonService(db).add_season(season_data=season_data)
    except ShowNotFoundException:
        raise ShowNotFoundHTTPException
    except UniqueSeasonPerShowException:
        raise SeasonAlreadyExistsHTTPException
    return {"status": "ok", "data": {"id": season_id}}


@v1_router.patch("/{season_id}", dependencies=[AdminDep])
async def update_season(db: DBDep, season_id: UUID, season_data: SeasonPatchRequestDTO):
    try:
        await SeasonService(db).update_season(season_id=season_id, season_data=season_data)
    except SeasonNotFoundException:
        raise SeasonNotFoundHTTPException
    except UniqueSeasonPerShowException:
        raise SeasonAlreadyExistsHTTPException
    return {"status": "ok"}


@v1_router.delete("/{season_id}", dependencies=[AdminDep], status_code=204)
async def delete_season(db: DBDep, season_id: UUID):
    await SeasonService(db).delete_season(season_id=season_id)
