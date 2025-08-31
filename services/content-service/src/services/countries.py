from src.exceptions import CountryNotFoundException, CountryAlreadyExistsException
from src.schemas.countries import CountryAddDTO, CountryAddRequestDTO
from src.services.base import BaseService


class CountryService(BaseService):
    async def get_countries(self, page: int, per_page: int):
        countries = await self.db.countries.get_filtered(page=page, per_page=per_page)
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

    async def delete_country(self, country_id: int):
        await self.db.countries.delete(id=country_id)
        await self.db.commit()
