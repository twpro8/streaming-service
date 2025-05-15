from pydantic import Field

from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import TitleStr, DurationInt, IDInt


class EpisodeDTO(BaseSchema):
    id: IDInt
    series_id: IDInt
    season_id: IDInt
    title: TitleStr
    episode_number: int = Field(ge=1, le=9999, title="Episode Number")
    duration: DurationInt
    file_id: IDInt | None


class EpisodeAddDTO(BaseSchema):
    series_id: IDInt
    season_id: IDInt
    title: TitleStr
    episode_number: int = Field(ge=1, le=9999, title="Episode Number")
    duration: DurationInt
    file_id: IDInt | None


class EpisodePatchRequestDTO(BaseSchema):
    series_id: IDInt | None
    season_id: IDInt | None
    title: TitleStr | None
    episode_number: int = Field(ge=1, le=9999, title="Episode Number")
    duration: DurationInt | None
    file_id: IDInt | None


class EpisodeDeleteRequestDTO(BaseSchema):
    series_id: IDInt
    season_id: IDInt
