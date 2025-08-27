from src.exceptions import CountryNotFoundException, CountryAlreadyExistsException
from src.schemas.countries import CountryAddDTO, CountryAddRequestDTO
from src.services.base import BaseService


class CountryService(BaseService):
    async def get_countries(self):
        countries = await self.db.countries.get_filtered()
        return countries

    async def get_country(self, country_id: int):
        country = await self.db.countries.get_one_or_none(id=country_id)
        if country is None:
            raise CountryNotFoundException
        return country

    async def add_country(self, country_data: CountryAddRequestDTO):
        _country_data = CountryAddDTO(
            code=country_data.code,
            name=country_data.name,
        )
        try:
            country_id = await self.db.countries.add_country(_country_data)
        except CountryAlreadyExistsException:
            raise
        await self.db.commit()
        return country_id

    async def update_country(self, country_id: int, country_data: CountryAddRequestDTO):
        if not await self.check_country_exists(id=country_id):
            raise CountryNotFoundException
        _country_data = CountryAddDTO(
            code=country_data.code,
            name=country_data.name,
        )
        try:
            await self.db.countries.update_country(
                country_id=country_id,
                data=_country_data,
            )
        except CountryAlreadyExistsException:
            raise
        await self.db.commit()

    async def delete_country(self, country_id: int):
        await self.db.countries.delete(id=country_id)
        await self.db.commit()
