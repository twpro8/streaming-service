from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.api.dependencies import PaginationDep, AdminDep
from src.exceptions import (
    DirectorNotFoundException,
    DirectorNotFoundHTTPException,
    DirectorAlreadyExistsException,
    DirectorAlreadyExistsHTTPException,
)
from src.factories.service import ServiceFactory
from src.schemas.directors import DirectorAddRequestDTO, DirectorPatchDTO
from src.services.directors import DirectorService


v1_router = APIRouter(prefix="/v1/directors", tags=["Directors"])


@v1_router.get("")
async def get_directors(
    service: Annotated[DirectorService, Depends(ServiceFactory.director_service_factory)],
    pagination: PaginationDep,
):
    directors = await service.get_directors(
        page=pagination.page,
        per_page=pagination.per_page,
    )
    return {"status": "ok", "data": directors}


@v1_router.get("/{director_id}")
async def get_director(
    service: Annotated[DirectorService, Depends(ServiceFactory.director_service_factory)],
    director_id: UUID,
):
    try:
        director = await service.get_director(director_id=director_id)
    except DirectorNotFoundException:
        raise DirectorNotFoundHTTPException
    return {"status": "ok", "data": director}


@v1_router.post("", dependencies=[AdminDep], status_code=201)
async def add_director(
    service: Annotated[DirectorService, Depends(ServiceFactory.director_service_factory)],
    director_data: DirectorAddRequestDTO,
):
    try:
        director_id = await service.add_director(director_data=director_data)
    except DirectorAlreadyExistsException:
        raise DirectorAlreadyExistsHTTPException
    return {"status": "ok", "data": {"id": director_id}}


@v1_router.patch("/{director_id}", dependencies=[AdminDep])
async def update_director(
    service: Annotated[DirectorService, Depends(ServiceFactory.director_service_factory)],
    director_id: UUID,
    director_data: DirectorPatchDTO,
):
    try:
        await service.update_director(
            director_id=director_id,
            director_data=director_data,
        )
    except DirectorNotFoundException:
        raise DirectorNotFoundHTTPException
    except DirectorAlreadyExistsException:
        raise DirectorAlreadyExistsHTTPException
    return {"status": "ok"}


@v1_router.delete("/{director_id}", dependencies=[AdminDep], status_code=204)
async def delete_director(
    service: Annotated[DirectorService, Depends(ServiceFactory.director_service_factory)],
    director_id: UUID,
):
    await service.delete_director(director_id=director_id)
