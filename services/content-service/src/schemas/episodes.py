from uuid import UUID

from pydantic import Field

from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import TitleStr, DurationInt, IDInt


class EpisodeDTO(BaseSchema):
    id: UUID
    series_id: UUID
    season_id: UUID
    title: TitleStr
    episode_number: int = Field(ge=1, le=9999, title="Episode Number")
    duration: DurationInt
    file_id: IDInt | None = None


class EpisodeAddDTO(BaseSchema):
    series_id: UUID
    season_id: UUID
    title: TitleStr
    episode_number: int = Field(ge=1, le=9999, title="Episode Number")
    duration: DurationInt
    file_id: IDInt | None = None


class EpisodePatchRequestDTO(BaseSchema):
    series_id: UUID | None = None
    season_id: UUID | None = None
    title: TitleStr | None = None
    episode_number: int = Field(None, ge=1, le=9999, title="Episode Number")
    duration: DurationInt | None = None
    file_id: IDInt | None = None


class EpisodeDeleteRequestDTO(BaseSchema):
    episode_id: UUID
    season_id: UUID
