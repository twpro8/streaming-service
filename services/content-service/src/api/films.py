from uuid import UUID

from fastapi import APIRouter

from src.schemas.films import FilmAddDTO, FilmPatchRequestDTO, FilmPutRequestDTO
from src.api.dependencies import DBDep, AdminDep, ContentParamsDep
from src.services.films import FilmService
from src.exceptions import (
    FilmNotFoundException,
    FilmNotFoundHTTPException,
    FilmAlreadyExistsException,
    FilmAlreadyExistsHTTPException,
    UniqueCoverURLException,
    UniqueVideoURLException,
    UniqueCoverURLHTTPException,
    UniqueVideoURLHTTPException,
)


router = APIRouter(prefix="/films", tags=["Films"])


@router.get("")
async def get_films(db: DBDep, common_params: ContentParamsDep):
    films = await FilmService(db).get_films(**common_params.model_dump())
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
    try:
        film = await FilmService(db).add_film(film_data)
    except FilmAlreadyExistsException:
        raise FilmAlreadyExistsHTTPException
    return {"status": "ok", "data": film}


@router.put("/{film_id}", dependencies=[AdminDep])
async def replace_film(db: DBDep, film_id: UUID, film_data: FilmPutRequestDTO):
    try:
        await FilmService(db).replace_film(film_id, film_data)
    except FilmNotFoundException:
        raise FilmNotFoundHTTPException
    except UniqueCoverURLException:
        raise UniqueCoverURLHTTPException
    except UniqueVideoURLException:
        raise UniqueVideoURLHTTPException
    return {"status": "ok"}


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
    return {"status": "ok"}


@router.delete("/{film_id}", status_code=204, dependencies=[AdminDep])
async def delete_film(db: DBDep, film_id: UUID):
    await FilmService(db).remove_film(film_id)
