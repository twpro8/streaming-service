from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Query

from src.exceptions import FilmNotFoundException, FilmNotFoundHTTPException
from src.schemas.films import FilmAddDTO, FilmPatchRequestDTO
from src.api.dependencies import DBDep, AdminDep, PaginationDep
from src.services.films import FilmService


router = APIRouter(prefix="/films", tags=["Films"])


@router.get("")
async def get_films(
        db: DBDep,
        pagination: PaginationDep,
        title: str | None = Query(None),
        description: str | None = Query(None),
        director: str | None = Query(None),
        release_year: date | None = Query(None),
        release_year_ge: date | None = Query(None),
        release_year_le: date | None = Query(None),
        rating: Decimal | None = Query(None, ge=0, le=10),
        rating_ge: Decimal | None = Query(None, ge=0, le=10),
        rating_le: Decimal | None = Query(None, ge=0, le=10),
):
    films = await FilmService(db).get_films(
        page=pagination.page,
        per_page=pagination.per_page,
        title=title,
        description=description,
        director=director,
        release_year=release_year,
        release_year_ge=release_year_ge,
        release_year_le=release_year_le,
        rating=rating,
        rating_ge=rating_ge,
        rating_le=rating_le,
    )
    return {"status": "ok", "data": films}


@router.get("/{film_id}")
async def get_film(db: DBDep, film_id: UUID):
    try:
        film = await FilmService(db).get_film(film_id=film_id)
    except FilmNotFoundException:
        raise FilmNotFoundHTTPException
    return {"status": "ok", "data": film}


@router.post("", dependencies=[AdminDep])
async def add_film(db: DBDep, film_data: FilmAddDTO):
    film = await FilmService(db).add_film(film_data)
    return {"status": "ok", "data": film}


@router.put("/{film_id}", dependencies=[AdminDep])
async def replace_film(db: DBDep, film_id: UUID, film_data: FilmAddDTO):
    try:
        await FilmService(db).replace_film(film_id, film_data)
    except FilmNotFoundException:
        raise FilmNotFoundHTTPException
    return {"status": "ok"}


@router.patch("/{film_id}", dependencies=[AdminDep])
async def update_film(db: DBDep, film_id: UUID, film_data: FilmPatchRequestDTO):
    try:
        await FilmService(db).update_film(film_id, film_data)
    except FilmNotFoundException:
        raise FilmNotFoundHTTPException
    return {"status": "ok"}


@router.delete("/{film_id}", status_code=204, dependencies=[AdminDep])
async def delete_film(db: DBDep, film_id: UUID):
    await FilmService(db).remove_film(film_id)
