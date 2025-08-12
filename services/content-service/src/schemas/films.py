from typing import List
from uuid import UUID

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, conint

from src.schemas.actors import ActorDTO
from src.schemas.base import BaseSchema, AtLeastOneFieldRequired
from src.schemas.genres import GenreDTO
from src.schemas.pydantic_types import (
    TitleStr,
    DurationInt,
    RatingDecimal,
    DescriptionStr,
    ReleaseYearDate,
    DirectorStr,
)


class FilmAddDTO(BaseModel):
    title: TitleStr
    description: DescriptionStr
    director: DirectorStr
    release_year: ReleaseYearDate
    duration: DurationInt
    cover_url: AnyUrl | None = None


class FilmAddRequestDTO(BaseSchema, FilmAddDTO):
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


class FilmDTO(FilmAddDTO):
    id: UUID
    rating: RatingDecimal
    video_url: AnyUrl | None = None


class FilmPatchDTO(BaseModel):
    title: TitleStr | None = None
    description: DescriptionStr | None = None
    director: DirectorStr | None = None
    release_year: ReleaseYearDate | None = None
    duration: DurationInt | None = None
    video_url: AnyUrl | None = None
    cover_url: AnyUrl | None = None


class FilmPatchRequestDTO(FilmPatchDTO, AtLeastOneFieldRequired):
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


class FilmWithRelsDTO(FilmDTO):
    genres: List[GenreDTO]
    actors: List[ActorDTO]
