from src.repositories.base import BaseRepository
from src.models.series import EpisodeORM
from src.schemas.episodes import EpisodeDTO
from src.repositories.mappers.mappers import EpisodeDataMapper


class EpisodeRepository(BaseRepository):
    model = EpisodeORM
    schema = EpisodeDTO
    mapper = EpisodeDataMapper

