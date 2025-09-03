from decimal import Decimal
from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, AnyUrl, ConfigDict, Field, conint

from src.schemas.actors import ActorDTO
from src.schemas.base import BaseSchema, AtLeastOneFieldMixin
from src.schemas.countries import CountryDTO
from src.schemas.directors import DirectorDTO
from src.schemas.genres import GenreDTO
from src.schemas.pydantic_types import Str256, Str1024, Date, StrAnyUrl


class ShowAddDTO(BaseModel):
    id: UUID
    title: Str256
    description: Str1024
    release_date: Date
    cover_url: StrAnyUrl | None = None


class ShowAddRequestDTO(BaseSchema):
    title: Str256
    description: Str1024
    release_date: Date
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


class ShowDTO(ShowAddDTO):
    rating: Decimal
    created_at: datetime
    updated_at: datetime


class ShowPatchDTO(BaseModel):
    title: Str256 | None = None
    description: Str1024 | None = None
    release_date: Date | None = None
    cover_url: StrAnyUrl | None = None


class ShowPatchRequestDTO(ShowPatchDTO, AtLeastOneFieldMixin):
    cover_url: AnyUrl | None = None
    directors_ids: List[conint(strict=True, ge=1)] | None = Field(
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
    genres_ids: List[conint(strict=True, ge=1)] = Field(
        default=None,
        examples=[
            [],
        ],
    )

    model_config = ConfigDict(extra="forbid")


class ShowWithRelsDTO(ShowDTO):
    directors: List[DirectorDTO]
    actors: List[ActorDTO]
    countries: List[CountryDTO]
    genres: List[GenreDTO]
