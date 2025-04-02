from typing import List

from fastapi import APIRouter, Query

from src.schemas.films import FilmAddDTO
from src.services.films import FilmService
from src.views.dependencies import DBDep


router = APIRouter(prefix="/films", tags=["Films"])


@router.get("")
async def get_films(db: DBDep, films_ids: List[int | None] = Query(None)):
    films = await FilmService(db).get_films(films_ids)
    return {"status": "success", "films": films}


@router.get("/{film_id}")
async def get_film(db: DBDep, film_id: int):
    film = await FilmService(db).get_film(film_id)
    return {"status": "success", "film": film}


@router.post("/")
async def add_film(db: DBDep, film_data: FilmAddDTO):
    film = await FilmService(db).add_film(film_data)
    return {"status": "success", "film": film}


@router.put("/{film_id}")
async def update_entire_film(db: DBDep, film_id: int): ...


@router.patch("/{film_id}")
async def partly_update_film(db: DBDep, film_id: int): ...


@router.delete("/{film_id}")
async def delete_film(db: DBDep, film_id: int): ...
