from typing import List

from src.exceptions import (
    ObjectAlreadyExistsException,
    AlreadyInFavoritesException,
    FavoriteNotFoundException,
    ContentNotFoundException,
)
from src.schemas.favorites import FavoriteAddDTO, FavoriteAddRequestDTO
from src.services.base import BaseService


class FavoriteService(BaseService):
    async def add_to_favorites(self, user_id: int, favorite: FavoriteAddRequestDTO):
        if not await self.check_content_exists(favorite.content_id, favorite.content_type):
            raise ContentNotFoundException

        favorite_to_add = FavoriteAddDTO(
            user_id=user_id, content_id=favorite.content_id, content_type=favorite.content_type
        )
        try:
            favorite = await self.db.favorites.add_one(favorite_to_add)
        except ObjectAlreadyExistsException:
            raise AlreadyInFavoritesException

        await self.db.commit()
        return favorite

    async def get_favorites(self, user_id: int, page: int, per_page: int) -> List:
        page = per_page * (page - 1)
        favorites = await self.db.favorites.get_favorites(
            user_id=user_id, page=page, per_page=per_page
        )
        return favorites

    async def remove_favorite(self, user_id: int, favorite_id: int) -> None:
        if not await self.check_favorite_exists(id=favorite_id, user_id=user_id):
            raise FavoriteNotFoundException

        await self.db.favorites.delete(user_id=user_id, id=favorite_id)
        await self.db.commit()
