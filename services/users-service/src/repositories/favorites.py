from typing import List

from sqlalchemy import select

from src.models import FavoritesORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import FavoritesDataMapper
from src.schemas.favorites import FavoriteDTO


class FavoritesRepository(BaseRepository):
    model = FavoritesORM
    schema = FavoriteDTO
    mapper = FavoritesDataMapper

    async def get_favorites_ids(self, user_id: int) -> List[int]:
        query = select(FavoritesORM.film_id).filter(FavoritesORM.user_id == user_id)
        favorites = (await self.session.execute(query)).scalars().all()
        return list(set(favorites))
