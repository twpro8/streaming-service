from typing import List
from uuid import UUID

from pydantic import BaseModel, AnyUrl, ConfigDict, Field, conint

from src.schemas.actors import ActorDTO
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
    genres_ids: List[conint(strict=True, ge=1)] | None = Field(
        default=None,
        examples=[
            [],
        ],
    )
    actors_ids: List[UUID] | None = Field(
        default=None,
        examples=[
            [],
        ],
    )


class SeriesDTO(SeriesAddDTO):
    id: UUID
    rating: RatingDecimal


class SeriesPatchDTO(BaseModel):
    title: TitleStr | None = None
    description: DescriptionStr | None = None
    director: DirectorStr | None = None
    release_year: ReleaseYearDate | None = None
    cover_url: AnyUrl | None = None


class SeriesPatchRequestDTO(SeriesPatchDTO, AtLeastOneFieldRequired):
    genres_ids: List[conint(strict=True, ge=1)] = Field(
        default=None,
        examples=[
            [],
        ],
    )
    actors_ids: List[UUID] | None = Field(
        default=None,
        examples=[
            [],
        ],
    )

    model_config = ConfigDict(extra="forbid")


class SeriesWithRelsDTO(SeriesDTO):
    genres: List[GenreDTO]
    actors: List[ActorDTO]
