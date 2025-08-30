from datetime import datetime
from uuid import UUID

from pydantic import AnyUrl

from src.schemas.base import BaseSchema, AtLeastOneFieldMixin
from src.schemas.pydantic_types import Str256, PositiveInt


class EpisodeAddRequestDTO(BaseSchema):
    show_id: UUID
    season_id: UUID
    title: Str256
    episode_number: PositiveInt
    duration: PositiveInt
    video_url: AnyUrl | None = None


class EpisodeAddDTO(EpisodeAddRequestDTO):
    id: UUID


class EpisodePatchRequestDTO(BaseSchema, AtLeastOneFieldMixin):
    title: Str256 | None = None
    episode_number: PositiveInt | None = None
    duration: PositiveInt | None = None
    video_url: AnyUrl | None = None


class EpisodeDTO(EpisodeAddDTO):
    created_at: datetime
    updated_at: datetime
