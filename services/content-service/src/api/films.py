from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Query

from src.schemas.films import FilmPatchRequestDTO, FilmAddRequestDTO
from src.api.dependencies import DBDep, AdminDep, ContentParamsDep, SortDep
from src.services.films import FilmService
from src.exceptions import (
    FilmNotFoundException,
    FilmNotFoundHTTPException,
    UniqueCoverURLException,
    UniqueVideoURLException,
    UniqueCoverURLHTTPException,
    UniqueVideoURLHTTPException,
    GenreNotFoundException,
    GenreNotFoundHTTPException,
    ActorNotFoundException,
    ActorNotFoundHTTPException,
)


router = APIRouter(prefix="/films", tags=["Films"])


@router.get("")
async def get_films(
    db: DBDep,
    common_params: ContentParamsDep,
    sort: SortDep,
    genres_ids: Annotated[List[int] | None, Query()] = None,
    actors_ids: Annotated[List[UUID] | None, Query()] = None,
):
    films = await FilmService(db).get_films(
        **common_params.model_dump(),
        genres_ids=genres_ids,
        actors_ids=actors_ids,
        sort_by=sort.field,
        sort_order=sort.order,
    )
    return {"status": "ok", "data": films}


@router.get("/{film_id}")
async def get_film(db: DBDep, film_id: UUID):
    try:
        film = await FilmService(db).get_film(film_id=film_id)
    except FilmNotFoundException:
        raise FilmNotFoundHTTPException
    return {"status": "ok", "data": film}


@router.post("", dependencies=[AdminDep], status_code=201)
async def add_film(db: DBDep, film_data: FilmAddRequestDTO):
    try:
        film_id = await FilmService(db).add_film(film_data)
    except UniqueCoverURLException:
        raise UniqueCoverURLHTTPException
    except GenreNotFoundException:
        raise GenreNotFoundHTTPException
    except ActorNotFoundException:
        raise ActorNotFoundHTTPException
    return {"status": "ok", "data": {"id": film_id}}


@router.patch("/{film_id}", dependencies=[AdminDep])
async def update_film(db: DBDep, film_id: UUID, film_data: FilmPatchRequestDTO):
    try:
        await FilmService(db).update_film(film_id, film_data)
    except FilmNotFoundException:
        raise FilmNotFoundHTTPException
    except UniqueCoverURLException:
        raise UniqueCoverURLHTTPException
    except UniqueVideoURLException:
        raise UniqueVideoURLHTTPException
    except GenreNotFoundException:
        raise GenreNotFoundHTTPException
    except ActorNotFoundException:
        raise ActorNotFoundHTTPException
    return {"status": "ok"}


@router.delete("/{film_id}", status_code=204, dependencies=[AdminDep])
async def delete_film(db: DBDep, film_id: UUID):
    await FilmService(db).remove_film(film_id)
