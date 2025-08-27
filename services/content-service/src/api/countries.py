from fastapi import APIRouter

from src.api.dependencies import DBDep
from src.exceptions import (
    CountryNotFoundException,
    CountryNotFoundHTTPException,
    CountryAlreadyExistsException,
    CountryAlreadyExistsHTTPException,
)
from src.schemas.countries import CountryAddRequestDTO
from src.services.countries import CountryService


v1_router = APIRouter(prefix="/v1/countries", tags=["countries"])


@v1_router.get("")
async def get_countries(db: DBDep):
    countries = await CountryService(db).get_countries()
    return {"status": "ok", "data": countries}


@v1_router.get("/{country_id}")
async def get_country(db: DBDep, country_id: int):
    try:
        country = await CountryService(db).get_country(country_id)
    except CountryNotFoundException:
        raise CountryNotFoundHTTPException
    return {"status": "ok", "data": country}


@v1_router.post("", status_code=201)
async def add_country(db: DBDep, country_data: CountryAddRequestDTO):
    try:
        country_id = await CountryService(db).add_country(country_data)
    except CountryAlreadyExistsException:
        raise CountryAlreadyExistsHTTPException
    return {"status": "ok", "data": {"id": country_id}}


@v1_router.put("/{country_id}")
async def update_country(db: DBDep, country_id: int, country_data: CountryAddRequestDTO):
    try:
        await CountryService(db).update_country(country_id, country_data)
    except CountryNotFoundException:
        raise CountryNotFoundHTTPException
    except CountryAlreadyExistsException:
        raise CountryAlreadyExistsHTTPException
    return {"status": "ok"}


@v1_router.delete("/{country_id}", status_code=204)
async def delete_country(db: DBDep, country_id: int):
    await CountryService(db).delete_country(country_id)
