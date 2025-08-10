from typing import List
from uuid import UUID

from pydantic import BaseModel, AnyUrl

from src.schemas.base import BaseSchema, AtLeastOneFieldRequired
from src.schemas.genres import GenreDTO
from src.schemas.pydantic_types import (
    TitleStr,
    RatingDecimal,
    DescriptionStr,
    DirectorStr,
    ReleaseYearDate,
)


class SeriesAddDTO(BaseModel):
    title: TitleStr
    description: DescriptionStr
    director: DirectorStr
    release_year: ReleaseYearDate
    cover_url: AnyUrl | None = None


class SeriesAddRequestDTO(BaseSchema, SeriesAddDTO):
    genres: List[int] = []


class SeriesDTO(SeriesAddDTO):
    id: UUID
    rating: RatingDecimal


class SeriesPatchRequestDTO(BaseSchema, AtLeastOneFieldRequired):
    title: TitleStr | None = None
    description: DescriptionStr | None = None
    director: DirectorStr | None = None
    release_year: ReleaseYearDate | None = None
    cover_url: AnyUrl | None = None


class SeriesWithRelsDTO(SeriesDTO):
    genres: List[GenreDTO]
