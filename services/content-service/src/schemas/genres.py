from uuid import UUID

from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import Str48


class GenreAddDTO(BaseSchema):
    name: Str48


class GenreDTO(GenreAddDTO):
    id: int


class MovieGenreDTO(BaseSchema):
    movie_id: UUID
    genre_id: int


class ShowGenreDTO(BaseSchema):
    show_id: UUID
    genre_id: int
