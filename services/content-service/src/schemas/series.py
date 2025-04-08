from datetime import date

from src.schemas.base import BaseSchema


class SeriesAddRequestDTO(BaseSchema):
    title: str
    description: str
    director: str
    release_year: date
    rating: float
    cover_id: int | None = None


class SeriesDTO(SeriesAddRequestDTO):
    id: int


class SeriesPatchRequestDTO(BaseSchema):
    title: str | None = None
    description: str | None = None
    director: str | None = None
    release_year: date | None = None
    rating: float | None = None
    cover_id: int | None = None


class SeriesPutRequestDTO(SeriesAddRequestDTO):
    pass
