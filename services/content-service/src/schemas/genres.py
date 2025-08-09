from uuid import UUID

from pydantic import Field

from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import IDInt


class GenreAddDTO(BaseSchema):
    name: str = Field(min_length=2, max_length=48)


class GenreDTO(GenreAddDTO):
    id: IDInt


class FilmGenreDTO(BaseSchema):
    film_id: UUID
    genre_id: IDInt


class SeriesGenreDTO(BaseSchema):
    series_id: UUID
    genre_id: IDInt
