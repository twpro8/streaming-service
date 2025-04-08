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


class FilmPatchRequestDTO(BaseSchema):
    title: str | None = None
    description: str | None = None
    director: str | None = None
    release_year: date | None = None
    rating: float | None = None
    duration: int | None = None
    file_id: int | None = None
    cover_id: int | None = None
