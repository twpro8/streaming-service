from uuid import UUID
from datetime import date

from pydantic import AnyUrl

from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import TitleStr, DurationInt, RatingDecimal, DescriptionStr


class FilmAddDTO(BaseSchema):
    title: TitleStr
    description: DescriptionStr
    director: str
    release_year: date
    duration: DurationInt
    video_url: AnyUrl | None = None
    cover_url: AnyUrl | None = None


class FilmDTO(FilmAddDTO):
    id: UUID
    rating: RatingDecimal


class FilmPatchRequestDTO(BaseSchema):
    title: TitleStr | None = None
    description: DescriptionStr | None = None
    director: str | None = None
    release_year: date | None = None
    duration: DurationInt | None = None
    video_url: AnyUrl | None = None
    cover_url: AnyUrl | None = None
