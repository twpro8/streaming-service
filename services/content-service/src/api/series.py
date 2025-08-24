from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Query

from src.exceptions import (
    SeriesNotFoundException,
    SeriesNotFoundHTTPException,
    UniqueCoverURLException,
    UniqueCoverURLHTTPException,
    GenreNotFoundException,
    GenreNotFoundHTTPException,
    ActorNotFoundException,
    ActorNotFoundHTTPException,
)
from src.schemas.series import SeriesAddRequestDTO, SeriesPatchRequestDTO
from src.services.series import SeriesService
from src.api.dependencies import DBDep, AdminDep, ContentParamsDep, SortDep


v1_router = APIRouter(prefix="/v1/series", tags=["Series"])


@v1_router.get("")
async def get_series(
    db: DBDep,
    common_params: ContentParamsDep,
    sort: SortDep,
    genres_ids: Annotated[List[int] | None, Query()] = None,
    actors_ids: Annotated[List[UUID] | None, Query()] = None,
):
    series = await SeriesService(db).get_series(
        **common_params.model_dump(),
        genres_ids=genres_ids,
        actors_ids=actors_ids,
        sort_by=sort.field,
        sort_order=sort.order,
    )
    return {"status": "ok", "data": series}


@v1_router.get("/{series_id}")
async def get_one_series(db: DBDep, series_id: UUID):
    try:
        series = await SeriesService(db).get_one_series(series_id)
    except SeriesNotFoundException:
        raise SeriesNotFoundHTTPException
    return {"status": "ok", "data": series}


@v1_router.post("", dependencies=[AdminDep], status_code=201)
async def add_series(db: DBDep, series_data: SeriesAddRequestDTO):
    try:
        series_id = await SeriesService(db).add_series(series_data)
    except UniqueCoverURLException:
        raise UniqueCoverURLHTTPException
    except GenreNotFoundException:
        raise GenreNotFoundHTTPException
    except ActorNotFoundException:
        raise ActorNotFoundHTTPException
    return {"status": "ok", "data": {"id": series_id}}


@v1_router.patch("/{series_id}", dependencies=[AdminDep])
async def update_series(db: DBDep, series_id: UUID, series_data: SeriesPatchRequestDTO):
    try:
        await SeriesService(db).update_series(series_id, series_data)
    except SeriesNotFoundException:
        raise SeriesNotFoundHTTPException
    except UniqueCoverURLException:
        raise UniqueCoverURLHTTPException
    except GenreNotFoundException:
        raise GenreNotFoundHTTPException
    except ActorNotFoundException:
        raise ActorNotFoundHTTPException
    return {"status": "ok"}


@v1_router.delete("/{series_id}", dependencies=[AdminDep], status_code=204)
async def delete_series(db: DBDep, series_id: UUID):
    await SeriesService(db).delete_series(series_id)
