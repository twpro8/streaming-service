from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models import PlaylistORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import (
    PlaylistDataMapper,
    PlaylistWithRelsDataMapper,
)
from src.schemas.playlists import PlaylistDTO


class PlaylistRepository(BaseRepository):
    model = PlaylistORM
    schema = PlaylistDTO
    mapper = PlaylistDataMapper

    async def get_playlist_with_items(self, **filter_by):
        query = select(PlaylistORM).options(selectinload(PlaylistORM.items)).filter_by(**filter_by)
        res = await self.session.execute(query)
        return [
            PlaylistWithRelsDataMapper.map_to_domain_entity(model) for model in res.scalars().all()
        ]
