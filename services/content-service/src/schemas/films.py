from typing import List
from uuid import UUID

from pydantic import AnyUrl

from src.schemas.base import BaseSchema, AtLeastOneFieldRequired
from src.schemas.pydantic_types import (
    TitleStr,
    DurationInt,
    RatingDecimal,
    DescriptionStr,
    ReleaseYearDate,
    DirectorStr,
)


class FilmAddDTO(BaseSchema):
    title: TitleStr
    description: DescriptionStr
    director: DirectorStr
    release_year: ReleaseYearDate
    duration: DurationInt
    cover_url: AnyUrl | None = None


class FilmAddRequestDTO(FilmAddDTO):
    genres: List[int] = []


class FilmDTO(FilmAddDTO):
    id: UUID
    rating: RatingDecimal
    video_url: AnyUrl | None = None


class FilmPatchRequestDTO(BaseSchema, AtLeastOneFieldRequired):
    title: TitleStr | None = None
    description: DescriptionStr | None = None
    director: DirectorStr | None = None
    release_year: ReleaseYearDate | None = None
    duration: DurationInt | None = None
    video_url: AnyUrl | None = None
    cover_url: AnyUrl | None = None
