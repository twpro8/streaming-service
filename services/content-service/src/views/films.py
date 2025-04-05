from typing import List

from fastapi import APIRouter, Query

from src.schemas.films import FilmAddDTO
from src.services.films import FilmService
from src.views.dependencies import DBDep, AdminDep


router = APIRouter(prefix="/films", tags=["Films"])


@router.get("")
async def get_films(db: DBDep, ids: List[int | None] = Query(...)):
    films = await FilmService(db).get_films(films_ids=ids)
    return {"status": "ok", "data": films}


@router.post("/", dependencies=[AdminDep])
async def add_film(db: DBDep, film_data: FilmAddDTO):
    film = await FilmService(db).add_film(film_data)
    return {"status": "ok", "data": film}


@router.put("/{film_id}", dependencies=[AdminDep])
async def update_entire_film(db: DBDep, film_id: int): ...


@router.patch("/{film_id}", dependencies=[AdminDep])
async def partly_update_film(db: DBDep, film_id: int): ...


@router.delete("/{film_id}", dependencies=[AdminDep])
async def delete_film(db: DBDep, film_id: int): ...
