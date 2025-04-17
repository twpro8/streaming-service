from datetime import date

from pydantic import BaseModel

from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import TypeID, TypeTitle, TypeDuration, TypeRating


class FilmDTO(BaseModel):
    id: TypeID
    title: TypeTitle
    description: str
    director: str
    release_year: date
    rating: TypeRating
    duration: TypeDuration
    file_id: TypeID
    cover_id: TypeID


class FilmAddDTO(BaseSchema):
    title: TypeTitle
    description: str
    director: str
    release_year: date
    rating: TypeRating
    duration: TypeDuration
    file_id: TypeID
    cover_id: TypeID


class FilmPatchRequestDTO(BaseSchema):
    title: TypeTitle | None
    description: str | None
    director: str | None
    release_year: date | None
    rating: TypeRating | None
    duration: TypeDuration | None
    file_id: TypeID | None
    cover_id: TypeID | None
