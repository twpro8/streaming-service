from fastapi import APIRouter

from src.api.dependencies import DBDep
from src.exceptions import (
    DirectorNotFoundException,
    DirectorNotFoundHTTPException,
    DirectorAlreadyExistsException,
    DirectorAlreadyExistsHTTPException,
)
from src.schemas.directors import DirectorAddDTO, DirectorPatchDTO
from src.services.directors import DirectorService


v1_router = APIRouter(prefix="/v1/directors", tags=["directors"])


@v1_router.get("")
async def get_directors(db: DBDep):
    directors = await DirectorService(db).get_directors()
    return {"status": "ok", "data": directors}


@v1_router.get("/{director_id}")
async def get_director(db: DBDep, director_id: int):
    try:
        director = await DirectorService(db).get_director(director_id)
    except DirectorNotFoundException:
        raise DirectorNotFoundHTTPException
    return {"status": "ok", "data": director}


@v1_router.post("", status_code=201)
async def add_director(db: DBDep, director_data: DirectorAddDTO):
    try:
        director_id = await DirectorService(db).add_director(director_data)
    except DirectorAlreadyExistsException:
        raise DirectorAlreadyExistsHTTPException
    return {"status": "ok", "data": {"id": director_id}}


@v1_router.patch("/{director_id}")
async def update_director(db: DBDep, director_id: int, director_data: DirectorPatchDTO):
    try:
        await DirectorService(db).update_director(director_id, director_data)
    except DirectorAlreadyExistsException:
        raise DirectorAlreadyExistsHTTPException
    return {"status": "ok"}


@v1_router.post("/{director_id}", status_code=204)
async def delete_director(db: DBDep, director_id: int):
    await DirectorService(db).delete_director(director_id)
