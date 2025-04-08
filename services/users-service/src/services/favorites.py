from typing import List

from src.exceptions import (
    ObjectAlreadyExistsException,
    AlreadyInFavoritesException,
    FavoriteNotFoundException,
    ObjectNotFoundException,
)
from src.schemas.favorites import FavoriteAddDTO, FavoriteAddRequestDTO, ContentType
from src.services.base import BaseService


class FavoriteService(BaseService):
    async def add_to_favorites(self, user_id: int, favorite: FavoriteAddRequestDTO):
        favorite_to_add = FavoriteAddDTO(
            user_id=user_id, content_id=favorite.content_id, content_type=favorite.content_type
        )
        try:
            favorite = await self.db.favorites.add_one(favorite_to_add)
        except ObjectAlreadyExistsException:
            raise AlreadyInFavoritesException

        await self.db.commit()
        return favorite

    async def get_favorites(self, user_id: int) -> List:
        films_ids = await self.db.favorites.get_ids(user_id=user_id, content_type="film")
        series_ids = await self.db.favorites.get_ids(user_id=user_id, content_type="series")

        films = (await self.adapter.content.get_films_by_ids(films_ids)).get("data", [])
        series = (await self.adapter.content.get_series_by_ids(series_ids)).get("data", [])

        content = films + series

        return content

    async def remove_favorite(self, user_id: int, favorite_id: int) -> None:
        try:
            await self.db.favorites.get_one(id=favorite_id, user_id=user_id)
        except ObjectNotFoundException:
            raise FavoriteNotFoundException
        await self.db.favorites.delete(id=favorite_id, user_id=user_id)
        await self.db.commit()
