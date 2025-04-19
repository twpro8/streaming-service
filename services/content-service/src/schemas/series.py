from datetime import date

from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import TypeID, TypeTitle, TypeRating


class SeriesAddRequestDTO(BaseSchema):
    title: TypeTitle
    description: str
    director: str
    release_year: date
    rating: TypeRating
    cover_id: int | None = None


class SeriesDTO(SeriesAddRequestDTO):
    id: TypeID


class SeriesPatchRequestDTO(BaseSchema):
    title: TypeTitle | None
    description: str | None
    director: str | None
    release_year: date | None
    rating: TypeRating | None
    cover_id: int | None


class SeriesPutRequestDTO(SeriesAddRequestDTO):
    pass
