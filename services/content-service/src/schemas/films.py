from uuid import UUID
from datetime import date

from pydantic import AnyUrl, Field

from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import TitleStr, DurationInt, RatingDecimal, DescriptionStr


class FilmAddDTO(BaseSchema):
    title: TitleStr
    description: DescriptionStr
    director: str = Field(default=None, min_length=3, max_length=255)
    release_year: date
    duration: DurationInt
    cover_url: AnyUrl | None = None


class FilmDTO(FilmAddDTO):
    id: UUID
    rating: RatingDecimal
    video_url: AnyUrl | None = None


class FilmPatchRequestDTO(BaseSchema):
    title: TitleStr | None = None
    description: DescriptionStr | None = None
    director: str | None = Field(default=None, min_length=3, max_length=255)
    release_year: date | None = None
    duration: DurationInt | None = None
    video_url: AnyUrl | None = None
    cover_url: AnyUrl | None = None


class FilmPutRequestDTO(FilmAddDTO):
    video_url: AnyUrl | None = None
