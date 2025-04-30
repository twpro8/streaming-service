from datetime import date

from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import TypeID, TypeTitle, TypeDuration, TypeRating


class FilmAddDTO(BaseSchema):
    title: TypeTitle
    description: str
    director: str
    release_year: date
    rating: TypeRating
    duration: TypeDuration
    file_id: TypeID
    cover_id: TypeID


class FilmDTO(FilmAddDTO):
    id: TypeID


class FilmPatchRequestDTO(BaseSchema):
    title: TypeTitle | None = None
    description: str | None = None
    director: str | None = None
    release_year: date | None = None
    rating: TypeRating | None = None
    duration: TypeDuration | None = None
    file_id: TypeID | None = None
    cover_id: TypeID | None = None
