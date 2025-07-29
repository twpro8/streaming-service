from uuid import UUID
from datetime import date

from pydantic import AnyUrl, Field

from src.schemas.base import BaseSchema, AtLeastOneFieldRequired
from src.schemas.pydantic_types import TitleStr, RatingDecimal, DescriptionStr


class SeriesAddRequestDTO(BaseSchema):
    title: TitleStr
    description: DescriptionStr
    director: str = Field(min_length=3, max_length=255)
    release_year: date
    cover_url: AnyUrl | None = None


class SeriesDTO(SeriesAddRequestDTO):
    id: UUID


class SeriesPatchRequestDTO(BaseSchema, AtLeastOneFieldRequired):
    title: TitleStr | None = None
    description: DescriptionStr | None = None
    director: str | None = Field(default=None, min_length=3, max_length=255)
    release_year: date | None = None
    rating: RatingDecimal | None = None
    cover_url: AnyUrl | None = None


class SeriesPutRequestDTO(SeriesAddRequestDTO):
    pass
