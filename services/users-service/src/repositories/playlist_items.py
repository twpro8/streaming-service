from src.models import PlaylistItemORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import PlaylistItemDataMapper
from src.schemas.playlists import PlaylistItemDTO


class PlaylistItemRepository(BaseRepository):
    model = PlaylistItemORM
    schema = PlaylistItemDTO
    mapper = PlaylistItemDataMapper
