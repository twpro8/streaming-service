from pydantic import Field

from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import TypeTitle, TypeDuration, TypeID


class EpisodeDTO(BaseSchema):
    id: TypeID
    series_id: TypeID
    season_id: TypeID
    title: TypeTitle
    episode_number: int = Field(ge=1, le=9999, title="Episode Number")
    duration: TypeDuration
    file_id: TypeID | None


class EpisodeAddDTO(BaseSchema):
    series_id: TypeID
    season_id: TypeID
    title: TypeTitle
    episode_number: int
    duration: TypeDuration
    file_id: TypeID | None


class EpisodePatchRequestDTO(BaseSchema):
    series_id: TypeID | None
    season_id: TypeID | None
    title: TypeTitle | None
    episode_number: int | None
    duration: TypeDuration | None
    file_id: TypeID | None


class EpisodeDeleteRequestDTO(BaseSchema):
    series_id: TypeID
    season_id: TypeID
