from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, conint

from src.schemas.actors import ActorDTO
from src.schemas.base import BaseSchema, AtLeastOneFieldMixin
from src.schemas.genres import GenreDTO
from src.schemas.pydantic_types import (
    TitleStr,
    DurationInt,
    RatingDecimal,
    DescriptionStr,
    ReleaseYearDate,
)


class MovieAddDTO(BaseModel):
    id: UUID
    title: TitleStr
    description: DescriptionStr
    release_year: ReleaseYearDate
    duration: DurationInt
    cover_url: AnyUrl | None = None


class MovieAddRequestDTO(BaseSchema):
    title: TitleStr
    description: DescriptionStr
    release_year: ReleaseYearDate
    duration: DurationInt
    cover_url: AnyUrl | None = None
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


class MovieDTO(MovieAddDTO):
    rating: RatingDecimal
    video_url: AnyUrl | None = None
    created_at: datetime
    updated_at: datetime


class MoviePatchDTO(BaseModel):
    title: TitleStr | None = None
    description: DescriptionStr | None = None
    release_year: ReleaseYearDate | None = None
    duration: DurationInt | None = None
    video_url: AnyUrl | None = None
    cover_url: AnyUrl | None = None


class MoviePatchRequestDTO(MoviePatchDTO, AtLeastOneFieldMixin):
    genres_ids: List[conint(strict=True, ge=1)] = Field(
        default=None,
        examples=[
            [],
        ],
    )
    actors_ids: List[UUID] = Field(
        default=None,
        examples=[
            [],
        ],
    )

    model_config = ConfigDict(extra="forbid")


class MovieWithRelsDTO(MovieDTO):
    genres: List[GenreDTO]
    actors: List[ActorDTO]
