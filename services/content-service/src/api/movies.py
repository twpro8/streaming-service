from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Query

from src.schemas.movies import MoviePatchRequestDTO, MovieAddRequestDTO
from src.api.dependencies import DBDep, AdminDep, ContentParamsDep, SortDep
from src.services.movies import MovieService
from src.exceptions import (
    MovieNotFoundException,
    MovieNotFoundHTTPException,
    UniqueCoverURLException,
    UniqueVideoURLException,
    UniqueCoverURLHTTPException,
    UniqueVideoURLHTTPException,
    GenreNotFoundException,
    GenreNotFoundHTTPException,
    ActorNotFoundException,
    ActorNotFoundHTTPException,
)


v1_router = APIRouter(prefix="/v1/movies", tags=["movies"])


@v1_router.get("")
async def get_movies(
    db: DBDep,
    common_params: ContentParamsDep,
    sort: SortDep,
    genres_ids: Annotated[List[int] | None, Query()] = None,
    actors_ids: Annotated[List[UUID] | None, Query()] = None,
):
    movies = await MovieService(db).get_movies(
        **common_params.model_dump(),
        genres_ids=genres_ids,
        actors_ids=actors_ids,
        sort_by=sort.field,
        sort_order=sort.order,
    )
    return {"status": "ok", "data": movies}


@v1_router.get("/{movie_id}")
async def get_movie(db: DBDep, movie_id: UUID):
    try:
        movie = await MovieService(db).get_movie(movie_id)
    except MovieNotFoundException:
        raise MovieNotFoundHTTPException
    return {"status": "ok", "data": movie}


@v1_router.post("", dependencies=[AdminDep], status_code=201)
async def add_movie(db: DBDep, movie_data: MovieAddRequestDTO):
    try:
        movie_id = await MovieService(db).add_movie(movie_data)
    except UniqueCoverURLException:
        raise UniqueCoverURLHTTPException
    except GenreNotFoundException:
        raise GenreNotFoundHTTPException
    except ActorNotFoundException:
        raise ActorNotFoundHTTPException
    return {"status": "ok", "data": {"id": movie_id}}


@v1_router.patch("/{movie_id}", dependencies=[AdminDep])
async def update_movie(db: DBDep, movie_id: UUID, movie_data: MoviePatchRequestDTO):
    try:
        await MovieService(db).update_movie(movie_id, movie_data)
    except MovieNotFoundException:
        raise MovieNotFoundHTTPException
    except UniqueCoverURLException:
        raise UniqueCoverURLHTTPException
    except UniqueVideoURLException:
        raise UniqueVideoURLHTTPException
    except GenreNotFoundException:
        raise GenreNotFoundHTTPException
    except ActorNotFoundException:
        raise ActorNotFoundHTTPException
    return {"status": "ok"}


@v1_router.delete("/{movie_id}", status_code=204, dependencies=[AdminDep])
async def delete_movie(db: DBDep, movie_id: UUID):
    await MovieService(db).delete_movie(movie_id)
