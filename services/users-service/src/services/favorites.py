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

    async def get_favorites(self, user_id: int) -> List:
        films_ids = await self.db.favorites.get_ids(user_id=user_id, content_type="films")
        series_ids = await self.db.favorites.get_ids(user_id=user_id, content_type="series")

        films = (await self.http_adapter.get_films_by_ids(films_ids)).get("data", [])
        series = (await self.http_adapter.get_series_by_ids(series_ids)).get("data", [])

        return films + series # TBI

    async def remove_favorite(self, user_id: int, favorite_id: int) -> None:
        exists = await self.db.favorites.get_one_or_none(id=favorite_id, user_id=user_id)
        if exists is None:
            raise FavoriteNotFoundException
        await self.db.favorites.delete(id=favorite_id, user_id=user_id)
        await self.db.commit()

    async def check_content_exists(self, content_id: int, content_type: str) -> bool:
        return await self.http_adapter.content_exists(content_id, content_type)
