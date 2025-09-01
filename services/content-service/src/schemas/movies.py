from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, conint

from src.schemas.actors import ActorDTO
from src.schemas.base import BaseSchema, AtLeastOneFieldMixin
from src.schemas.countries import CountryDTO
from src.schemas.directors import DirectorDTO
from src.schemas.genres import GenreDTO
from src.schemas.pydantic_types import RatingDecimal, Str256, Str1024, Date, PositiveInt


class MovieAddDTO(BaseModel):
    id: UUID
    title: Str256
    description: Str1024
    release_date: Date
    duration: PositiveInt
    cover_url: AnyUrl | None = None


class MovieAddRequestDTO(BaseSchema):
    title: Str256
    description: Str1024
    release_date: Date
    duration: PositiveInt
    cover_url: AnyUrl | None = None
    directors_ids: List[UUID] | None = Field(
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
    countries_ids: List[conint(strict=True, ge=1)] | None = Field(
        default=None,
        examples=[
            [],
        ],
    )
    genres_ids: List[conint(strict=True, ge=1)] | None = Field(
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
    title: Str256 | None = None
    description: Str1024 | None = None
    release_date: Date | None = None
    duration: PositiveInt | None = None
    video_url: AnyUrl | None = None
    cover_url: AnyUrl | None = None


class MoviePatchRequestDTO(MoviePatchDTO, AtLeastOneFieldMixin):
    directors_ids: List[conint(strict=True, ge=1)] | None = Field(
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
    countries_ids: List[conint(strict=True, ge=1)] | None = Field(
        default=None,
        examples=[
            [],
        ],
    )
    genres_ids: List[conint(strict=True, ge=1)] = Field(
        default=None,
        examples=[
            [],
        ],
    )

    model_config = ConfigDict(extra="forbid")


class MovieWithRelsDTO(MovieDTO):
    directors: List[DirectorDTO]
    actors: List[ActorDTO]
    countries: List[CountryDTO]
    genres: List[GenreDTO]
