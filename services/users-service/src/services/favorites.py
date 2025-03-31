from src.schemas.favorites import FavoriteAddDTO
from src.services.base import BaseService


class FavoriteService(BaseService):
    async def add_to_favorites(self, user_id: int, film_id: int):
        favorite_to_add = FavoriteAddDTO(user_id=user_id, film_id=film_id)
        favorite = await self.db.favorites.add_one(favorite_to_add)
        await self.db.commit()
        return favorite

    async def get_my_favorites(self, user_id: int):
        favorites = await self.db.favorites.get_filtered(user_id=user_id)
        return favorites
