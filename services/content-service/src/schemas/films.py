from datetime import date

from pydantic import BaseModel

from src.schemas.base import BaseSchema


class FilmDTO(BaseModel):
    id: int
    title: str
    description: str
    director: str
    release_year: date
    rating: float
    duration: int
    file_id: int
    cover_id: int


class FilmAddDTO(BaseSchema):
    title: str
    description: str
    director: str
    release_year: date
    rating: float
    duration: int
    file_id: int
    cover_id: int
