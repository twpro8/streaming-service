from uuid import UUID

from datetime import date

from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import IDInt, TitleStr, DurationInt, RatingDecimal, DescriptionStr


class FilmAddDTO(BaseSchema):
    title: TitleStr
    description: DescriptionStr
    director: str
    release_year: date
    duration: DurationInt
    file_id: IDInt
    cover_id: IDInt


class FilmDTO(FilmAddDTO):
    id: UUID
    rating: RatingDecimal


class FilmPatchRequestDTO(BaseSchema):
    title: TitleStr | None = None
    description: DescriptionStr | None = None
    director: str | None = None
    release_year: date | None = None
    duration: DurationInt | None = None
    file_id: IDInt | None = None
    cover_id: IDInt | None = None
