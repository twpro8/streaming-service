from typing import List

from sqlalchemy import select

from src.models import FavoritesORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import FavoritesDataMapper
from src.schemas.favorites import FavoriteDTO, ContentType


class FavoritesRepository(BaseRepository):
    model = FavoritesORM
    schema = FavoriteDTO
    mapper = FavoritesDataMapper

    async def get_ids(self, user_id: int, content_type: ContentType) -> List[int]:
        query = select(FavoritesORM.content_id).filter(
            FavoritesORM.user_id == user_id, FavoritesORM.content_type == content_type
        )
        ids = (await self.session.execute(query)).scalars().all()
        return ids
