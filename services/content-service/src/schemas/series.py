from uuid import UUID

from datetime import date

from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import TitleStr, RatingDecimal, DescriptionStr


class SeriesAddRequestDTO(BaseSchema):
    title: TitleStr
    description: DescriptionStr
    director: str
    release_year: date
    rating: RatingDecimal
    cover_id: int | None = None


class SeriesDTO(SeriesAddRequestDTO):
    id: UUID


class SeriesPatchRequestDTO(BaseSchema):
    title: TitleStr | None = None
    description: DescriptionStr | None = None
    director: str | None = None
    release_year: date | None = None
    rating: RatingDecimal | None = None
    cover_id: int | None = None


class SeriesPutRequestDTO(SeriesAddRequestDTO):
    pass
