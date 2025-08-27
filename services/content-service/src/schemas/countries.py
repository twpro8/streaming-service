from uuid import UUID

import pycountry
from pydantic_extra_types.country import CountryAlpha2, CountryShortName

from src.schemas.base import BaseSchema


class CountryAddRequestDTO(BaseSchema):
    code: CountryAlpha2

    @property
    def name(self) -> CountryShortName:
        return pycountry.countries.get(alpha_2=self.code).name


class CountryAddDTO(BaseSchema):
    code: CountryAlpha2
    name: CountryShortName


class CountryDTO(CountryAddDTO):
    id: int


class MovieCountryDTO(BaseSchema):
    movie_id: UUID
    country_id: int


class ShowCountryDTO(BaseSchema):
    show_id: UUID
    country_id: int
