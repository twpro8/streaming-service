from typing import List

from src.exceptions import (
    ObjectAlreadyExistsException,
    PlaylistAlreadyExistsException,
    PlaylistNotFoundException,
    PlaylistItemAlreadyExistsException,
    PlaylistItemNotFoundException,
)
from src.schemas.playlists import (
    PlaylistAddDTO,
    PlaylistAddRequestDTO,
    PlaylistDTO,
    PlaylistItemDTO,
    PlaylistItemAddRequestDTO,
    PlaylistItemAddDTO,
)
from src.services.base import BaseService


class PlaylistService(BaseService):
    async def get_playlists(self, user_id: int, page: int, per_page: int) -> List[PlaylistDTO]:
        playlists = await self.db.playlists.get_filtered(
            user_id=user_id, limit=per_page, offset=per_page * (page - 1)
        )
        return playlists

    async def get_items(
        self, user_id: int, playlist_id: int, page: int, per_page: int
    ) -> List[PlaylistItemDTO]:
        if not await self.check_playlist_exists(id=playlist_id, user_id=user_id):
            raise PlaylistNotFoundException

        items = await self.db.playlist_items.get_filtered(
            playlist_id=playlist_id, limit=per_page, offset=per_page * (page - 1)
        )
        return items

    async def add_playlist(self, user_id: int, data: PlaylistAddRequestDTO) -> PlaylistDTO:
        new_data = PlaylistAddDTO(user_id=user_id, name=data.name)
        try:
            playlist = await self.db.playlists.add_one(data=new_data)
        except ObjectAlreadyExistsException:
            raise PlaylistAlreadyExistsException

        await self.db.commit()
        return playlist

    async def add_item(
        self, user_id: int, playlist_id: int, data: PlaylistItemAddRequestDTO
    ) -> PlaylistItemDTO:
        if not await self.check_playlist_exists(id=playlist_id, user_id=user_id):
            raise PlaylistNotFoundException

        new_data = PlaylistItemAddDTO(
            playlist_id=playlist_id, content_id=data.content_id, content_type=data.content_type
        )
        try:
            item = await self.db.playlist_items.add_one(data=new_data)
        except ObjectAlreadyExistsException:
            raise PlaylistItemAlreadyExistsException

        await self.db.commit()
        return item

    async def remove_playlist(self, user_id: int, playlist_id: int) -> None:
        if not await self.check_playlist_exists(id=playlist_id, user_id=user_id):
            raise PlaylistNotFoundException

        await self.db.playlists.delete(id=playlist_id, user_id=user_id)
        await self.db.commit()

    async def remove_item(self, user_id: int, playlist_id: int, item_id: int) -> None:
        if not await self.check_playlist_exists(id=playlist_id, user_id=user_id):
            raise PlaylistNotFoundException
        if not await self.check_item_exists(id=item_id, playlist_id=playlist_id):
            raise PlaylistItemNotFoundException

        await self.db.playlist_items.delete(id=item_id, playlist_id=playlist_id)
        await self.db.commit()
