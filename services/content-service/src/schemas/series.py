from datetime import date

from src.schemas.base import BaseSchema


class SeriesAddRequestDTO(BaseSchema):
    title: str
    description: str
    director: str
    release_year: date
    rating: float
    cover_id: int


class SeriesDTO(SeriesAddRequestDTO):
    id: int
