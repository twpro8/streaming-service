from pydantic import BaseModel


class EpisodeDTO(BaseModel):
    id: int
    series_id: int
    season_id: int
    title: str
    episode_number: int
    duration: int
    file_id: int | None = None

