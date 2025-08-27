from uuid import UUID

import pycountry
from pydantic_extra_types.country import CountryAlpha2

from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import IDInt, Str100


class CountryAddRequestDTO(BaseSchema):
    code: CountryAlpha2

    @property
    def name(self) -> str:
        country = pycountry.countries.get(alpha_2=self.code)
        if not country:
            return "Unknown"
        return country.name


class CountryAddDTO(BaseSchema):
    code: CountryAlpha2
    name: Str100


class CountryDTO(CountryAddDTO):
    id: IDInt


class CountryPutDTO(BaseSchema):
    code: CountryAlpha2
    name: Str100


class MovieCountryDTO(BaseSchema):
    movie_id: UUID
    country_id: IDInt


class ShowCountryDTO(BaseSchema):
    show_id: UUID
    country_id: IDInt
