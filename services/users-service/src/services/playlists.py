from typing import List

from src.exceptions import (
    ObjectAlreadyExistsException,
    PlaylistAlreadyExistsException,
    PlaylistNotFoundException
)
from src.schemas.playlists import PlaylistAddDTO, PlaylistAddRequestDTO, PlaylistDTO
from src.services.base import BaseService


class PlaylistService(BaseService):
    async def get_playlists(self, user_id: int, page: int, per_page: int) -> List[PlaylistDTO]:
        offset = per_page * (page - 1)
        playlists = await self.db.playlists.get_filtered(user_id=user_id, limit=per_page, offset=offset)
        return playlists

    async def add_playlist(self, user_id: int, data: PlaylistAddRequestDTO) -> PlaylistDTO:
        new_data = PlaylistAddDTO(user_id=user_id, name=data.name)
        try:
            playlist = await self.db.playlists.add_one(data=new_data)
        except ObjectAlreadyExistsException:
            raise PlaylistAlreadyExistsException

        await self.db.commit()
        return playlist

    async def remove_playlist(self, user_id: int, playlist_id: int) -> None:
        if not await self.check_playlist_exists(id=playlist_id):
            raise PlaylistNotFoundException

        await self.db.playlists.delete(id=playlist_id, user_id=user_id)
        await self.db.commit()
