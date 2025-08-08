from pydantic import Field

from src.schemas.base import BaseSchema


class GenreAddDTO(BaseSchema):
    name: str = Field(min_length=2, max_length=48)


class GenreDTO(GenreAddDTO):
    id: int
