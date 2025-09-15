from typing import Annotated

from fastapi import APIRouter, Depends

from src.api.dependencies import PaginationDep, AdminDep
from src.exceptions import (
    CountryNotFoundException,
    CountryNotFoundHTTPException,
    CountryAlreadyExistsException,
    CountryAlreadyExistsHTTPException,
)
from src.factories.service import ServiceFactory
from src.schemas.countries import CountryAddRequestDTO
from src.services.countries import CountryService


v1_router = APIRouter(prefix="/v1/countries", tags=["countries"])


@v1_router.get("")
async def get_countries(
    service: Annotated[CountryService, Depends(ServiceFactory.country_service_factory)],
    pagination: PaginationDep,
):
    countries = await service.get_countries(
        page=pagination.page,
        per_page=pagination.per_page,
    )
    return {"status": "ok", "data": countries}


@v1_router.get("/{country_id}")
async def get_country(
    service: Annotated[CountryService, Depends(ServiceFactory.country_service_factory)],
    country_id: int,
):
    try:
        country = await service.get_country(country_id=country_id)
    except CountryNotFoundException:
        raise CountryNotFoundHTTPException
    return {"status": "ok", "data": country}


@v1_router.post("", dependencies=[AdminDep], status_code=201)
async def add_country(
    service: Annotated[CountryService, Depends(ServiceFactory.country_service_factory)],
    country_data: CountryAddRequestDTO,
):
    try:
        country_id = await service.add_country(country_data=country_data)
    except CountryAlreadyExistsException:
        raise CountryAlreadyExistsHTTPException
    return {"status": "ok", "data": {"id": country_id}}


@v1_router.delete("/{country_id}", dependencies=[AdminDep], status_code=204)
async def delete_country(
    service: Annotated[CountryService, Depends(ServiceFactory.country_service_factory)],
    country_id: int,
):
    await service.delete_country(country_id=country_id)
