from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Query, Depends

from src.factories.service import ServiceFactory
from src.schemas.movies import MoviePatchRequestDTO, MovieAddRequestDTO
from src.api.dependencies import AdminDep, ContentParamsDep, SortDep
from src.services.movies import MovieService


v1_router = APIRouter(prefix="/v1/movies", tags=["Movies"])


@v1_router.get("")
async def get_movies(
    service: Annotated[MovieService, Depends(ServiceFactory.movie_service_factory)],
    common_params: ContentParamsDep,
    sort: SortDep,
    directors_ids: Annotated[List[UUID] | None, Query()] = None,
    actors_ids: Annotated[List[UUID] | None, Query()] = None,
    genres_ids: Annotated[List[int] | None, Query()] = None,
    countries_ids: Annotated[List[int] | None, Query()] = None,
):
    movies = await service.get_movies(
        directors_ids=directors_ids,
        actors_ids=actors_ids,
        genres_ids=genres_ids,
        countries_ids=countries_ids,
        sort_by=sort.field,
        sort_order=sort.order,
        **common_params.model_dump(),
    )
    return {"status": "ok", "data": movies}


@v1_router.get("/{movie_id}")
async def get_movie(
    service: Annotated[MovieService, Depends(ServiceFactory.movie_service_factory)],
    movie_id: UUID,
):
    movie = await service.get_movie(movie_id=movie_id)
    return {"status": "ok", "data": movie}


@v1_router.post("", dependencies=[AdminDep], status_code=201)
async def add_movie(
    service: Annotated[MovieService, Depends(ServiceFactory.movie_service_factory)],
    movie_data: MovieAddRequestDTO,
):
    movie_id = await service.add_movie(movie_data=movie_data)
    return {"status": "ok", "data": {"id": movie_id}}


@v1_router.patch("/{movie_id}", dependencies=[AdminDep])
async def update_movie(
    service: Annotated[MovieService, Depends(ServiceFactory.movie_service_factory)],
    movie_id: UUID,
    movie_data: MoviePatchRequestDTO,
):
    await service.update_movie(movie_id=movie_id, movie_data=movie_data)
    return {"status": "ok"}


@v1_router.delete("/{movie_id}", status_code=204, dependencies=[AdminDep])
async def delete_movie(
    service: Annotated[MovieService, Depends(ServiceFactory.movie_service_factory)],
    movie_id: UUID,
):
    await service.delete_movie(movie_id=movie_id)
