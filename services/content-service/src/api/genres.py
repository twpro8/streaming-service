from fastapi import APIRouter

from src.api.dependencies import DBDep, PaginationDep, AdminDep
from src.exceptions import (
    GenreNotFoundException,
    GenreNotFoundHTTPException,
    GenreAlreadyExistsException,
    GenreAlreadyExistsHTTPException,
)
from src.schemas.genres import GenreAddDTO
from src.schemas.pydantic_types import IDInt
from src.services.genres import GenreService


v1_router = APIRouter(prefix="/v1/genres", tags=["Genres"])


@v1_router.get("")
async def get_genres(db: DBDep, pagination: PaginationDep):
    genres = await GenreService(db).get_genres(
        per_page=pagination.per_page,
        page=pagination.page,
    )
    return {"status": "ok", "data": genres}


@v1_router.get("/{genre_id}")
async def get_genre(db: DBDep, genre_id: IDInt):
    try:
        genre = await GenreService(db).get_genre(genre_id=genre_id)
    except GenreNotFoundException:
        raise GenreNotFoundHTTPException
    return {"status": "ok", "data": genre}


@v1_router.post("", dependencies=[AdminDep], status_code=201)
async def add_genre(db: DBDep, genre_data: GenreAddDTO):
    try:
        genre_id = await GenreService(db).add_genre(genre_data=genre_data)
    except GenreAlreadyExistsException:
        raise GenreAlreadyExistsHTTPException
    return {"status": "ok", "data": {"id": genre_id}}


@v1_router.delete("/{genre_id}", dependencies=[AdminDep], status_code=204)
async def delete_genre(db: DBDep, genre_id: IDInt):
    await GenreService(db).delete_genre(genre_id=genre_id)
