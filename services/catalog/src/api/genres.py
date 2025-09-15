from typing import Annotated

from fastapi import APIRouter, Depends

from src.api.dependencies import PaginationDep, AdminDep
from src.exceptions import (
    GenreNotFoundException,
    GenreNotFoundHTTPException,
    GenreAlreadyExistsException,
    GenreAlreadyExistsHTTPException,
)
from src.factories.service import ServiceFactory
from src.schemas.genres import GenreAddDTO
from src.services.genres import GenreService


v1_router = APIRouter(prefix="/v1/genres", tags=["genres"])


@v1_router.get("")
async def get_genres(
    service: Annotated[GenreService, Depends(ServiceFactory.genre_service_factory)],
    pagination: PaginationDep,
):
    genres = await service.get_genres(
        per_page=pagination.per_page,
        page=pagination.page,
    )
    return {"status": "ok", "data": genres}


@v1_router.get("/{genre_id}")
async def get_genre(
    service: Annotated[GenreService, Depends(ServiceFactory.genre_service_factory)],
    genre_id: int,
):
    try:
        genre = await service.get_genre(genre_id=genre_id)
    except GenreNotFoundException:
        raise GenreNotFoundHTTPException
    return {"status": "ok", "data": genre}


@v1_router.post("", dependencies=[AdminDep], status_code=201)
async def add_genre(
    service: Annotated[GenreService, Depends(ServiceFactory.genre_service_factory)],
    genre_data: GenreAddDTO,
):
    try:
        genre_id = await service.add_genre(genre_data=genre_data)
    except GenreAlreadyExistsException:
        raise GenreAlreadyExistsHTTPException
    return {"status": "ok", "data": {"id": genre_id}}


@v1_router.delete("/{genre_id}", dependencies=[AdminDep], status_code=204)
async def delete_genre(
    service: Annotated[GenreService, Depends(ServiceFactory.genre_service_factory)],
    genre_id: int,
):
    await service.delete_genre(genre_id=genre_id)
