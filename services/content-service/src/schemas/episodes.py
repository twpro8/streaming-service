from src.schemas.base import BaseSchema


class EpisodeDTO(BaseSchema):
    id: int
    series_id: int
    season_id: int
    title: str
    episode_number: int
    duration: int
    file_id: int | None = None


class EpisodeAddDTO(BaseSchema):
    series_id: int
    season_id: int
    title: str
    episode_number: int
    duration: int
    file_id: int | None = None


class EpisodePatchRequestDTO(BaseSchema):
    series_id: int | None = None
    season_id: int | None = None
    title: str | None = None
    episode_number: int | None = None
    duration: int | None = None
    file_id: int | None = None

