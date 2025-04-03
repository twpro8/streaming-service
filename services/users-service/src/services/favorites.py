from src.config import settings
from src.exceptions import (
    FilmNotFoundException,
    ObjectAlreadyExistsException,
    AlreadyInFavoritesException,
)
from src.schemas.favorites import FavoriteAddDTO
from src.services.base import BaseService


class FavoriteService(BaseService):
    async def add_to_favorites(self, user_id: int, film_id: int):
        try:
            film_exists = await self.ac.get(f"{settings.CONTENT_SERVICE_URL}/films/{film_id}")
            if film_exists.status_code != 200:
                raise FilmNotFoundException

            favorite_to_add = FavoriteAddDTO(user_id=user_id, film_id=film_id)
            favorite = await self.db.favorites.add_one(favorite_to_add)
        except ObjectAlreadyExistsException:
            raise AlreadyInFavoritesException

        await self.db.commit()
        return favorite

    async def get_favorites(self, user_id: int):
        films_ids = await self.db.favorites.get_favorites_ids(user_id)
        if films_ids:
            films = (
                await self.ac.get(
                    f"{settings.CONTENT_SERVICE_URL}/films",
                    params=[("films_ids", film_id) for film_id in films_ids],
                )
            ).json()["films"]
            return films
        return []
