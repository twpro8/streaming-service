from src.exceptions import (
    ObjectAlreadyExistsException,
    AlreadyInFavoritesException,
)
from src.schemas.favorites import FavoriteAddDTO, FavoriteAddRequestDTO
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

    async def get_favorites(self, user_id: int):
        films_ids = await self.db.favorites.get_ids(user_id=user_id, content_type="film")
        films = (await self.adapter.content.get_films_by_ids(films_ids)).get("films")

        return films

    async def remove_favorite(self, film_id: int) -> None: ...
