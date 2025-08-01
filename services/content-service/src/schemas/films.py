from uuid import UUID
from datetime import date

from pydantic import AnyUrl, Field

from src.schemas.base import BaseSchema, AtLeastOneFieldRequired
from src.schemas.pydantic_types import TitleStr, DurationInt, RatingDecimal, DescriptionStr


class FilmAddDTO(BaseSchema):
    title: TitleStr
    description: DescriptionStr
    director: str = Field(default=None, min_length=3, max_length=48)
    release_year: date = Field(le=date.today(), ge=date(1000, 1, 1))
    duration: DurationInt
    cover_url: AnyUrl | None = None


class FilmDTO(FilmAddDTO):
    id: UUID
    rating: RatingDecimal
    video_url: AnyUrl | None = None


class FilmPatchRequestDTO(BaseSchema, AtLeastOneFieldRequired):
    title: TitleStr | None = None
    description: DescriptionStr | None = None
    director: str | None = Field(default=None, min_length=3, max_length=48)
    release_year: date | None = Field(default=None, le=date.today(), ge=date(1000, 1, 1))
    duration: DurationInt | None = None
    video_url: AnyUrl | None = None
    cover_url: AnyUrl | None = None
