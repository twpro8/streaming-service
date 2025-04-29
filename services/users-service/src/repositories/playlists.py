from src.models import PlaylistORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import PlaylistDataMapper
from src.schemas.playlists import PlaylistDTO


class PlaylistRepository(BaseRepository):
    model = PlaylistORM
    schema = PlaylistDTO
    mapper = PlaylistDataMapper
