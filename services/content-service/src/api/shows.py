from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Query

from src.exceptions import (
    ShowNotFoundException,
    ShowNotFoundHTTPException,
    UniqueCoverURLException,
    UniqueCoverURLHTTPException,
    GenreNotFoundException,
    GenreNotFoundHTTPException,
    ActorNotFoundException,
    ActorNotFoundHTTPException,
    DirectorNotFoundException,
    DirectorNotFoundHTTPException,
    CountryNotFoundException,
    CountryNotFoundHTTPException,
    ShowAlreadyExistsException,
    ShowAlreadyExistsHTTPException,
)
from src.schemas.shows import ShowAddRequestDTO, ShowPatchRequestDTO
from src.services.shows import ShowService
from src.api.dependencies import DBDep, AdminDep, ContentParamsDep, SortDep


v1_router = APIRouter(prefix="/v1/shows", tags=["shows"])


@v1_router.get("")
async def get_shows(
    db: DBDep,
    common_params: ContentParamsDep,
    sort: SortDep,
    directors_ids: Annotated[List[UUID] | None, Query()] = None,
    actors_ids: Annotated[List[UUID] | None, Query()] = None,
    genres_ids: Annotated[List[int] | None, Query()] = None,
    countries_ids: Annotated[List[int] | None, Query()] = None,
):
    shows = await ShowService(db).get_shows(
        **common_params.model_dump(),
        directors_ids=directors_ids,
        actors_ids=actors_ids,
        genres_ids=genres_ids,
        countries_ids=countries_ids,
        sort_by=sort.field,
        sort_order=sort.order,
    )
    return {"status": "ok", "data": shows}


@v1_router.get("/{show_id}")
async def get_show(db: DBDep, show_id: UUID):
    try:
        show = await ShowService(db).get_show(show_id)
    except ShowNotFoundException:
        raise ShowNotFoundHTTPException
    return {"status": "ok", "data": show}


@v1_router.post("", dependencies=[AdminDep], status_code=201)
async def add_show(db: DBDep, show_data: ShowAddRequestDTO):
    try:
        show_id = await ShowService(db).add_show(show_data)
    except ShowAlreadyExistsException:
        raise ShowAlreadyExistsHTTPException
    except UniqueCoverURLException:
        raise UniqueCoverURLHTTPException
    except GenreNotFoundException:
        raise GenreNotFoundHTTPException
    except ActorNotFoundException:
        raise ActorNotFoundHTTPException
    except DirectorNotFoundException:
        raise DirectorNotFoundHTTPException
    except CountryNotFoundException:
        raise CountryNotFoundHTTPException
    return {"status": "ok", "data": {"id": show_id}}


@v1_router.patch("/{show_id}", dependencies=[AdminDep])
async def update_show(db: DBDep, show_id: UUID, show_data: ShowPatchRequestDTO):
    try:
        await ShowService(db).update_show(show_id, show_data)
    except ShowNotFoundException:
        raise ShowNotFoundHTTPException
    except UniqueCoverURLException:
        raise UniqueCoverURLHTTPException
    except GenreNotFoundException:
        raise GenreNotFoundHTTPException
    except ActorNotFoundException:
        raise ActorNotFoundHTTPException
    except DirectorNotFoundException:
        raise DirectorNotFoundHTTPException
    except CountryNotFoundException:
        raise CountryNotFoundHTTPException
    return {"status": "ok"}


@v1_router.delete("/{show_id}", dependencies=[AdminDep], status_code=204)
async def delete_show(db: DBDep, show_id: UUID):
    await ShowService(db).delete_show(show_id)
