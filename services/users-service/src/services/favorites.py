from pydantic import BaseModel
from typing import List

from src.exceptions import (
    ObjectAlreadyExistsException,
    AlreadyInFavoritesException,
    FavoriteNotFoundException,
    ContentNotFoundException,
)
from src.schemas.favorites import FavoriteAddDTO, FavoriteAddRequestDTO, FavoriteResponseDTO
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

        films_ids = [fav.content_id for fav in favorites if fav.content_type == "films"]
        series_ids = [fav.content_id for fav in favorites if fav.content_type == "series"]
        films = await self.http_adapter.get_content_by_ids(films_ids, "films")
        series = await self.http_adapter.get_content_by_ids(series_ids, "series")

        mapper = {(item["id"], "films"): item for item in films}
        mapper.update({(item["id"], "series"): item for item in series})

        favorites_data = [
            FavoriteResponseDTO(
                id=fav.content_id,
                cover_id=mapper[(fav.content_id, fav.content_type)]["cover_id"],
                content_type=fav.content_type,
                title=mapper[(fav.content_id, fav.content_type)]["title"],
                rating=mapper[(fav.content_id, fav.content_type)]["rating"],
                created_at=fav.created_at,
            )
            for fav in favorites
            if (fav.content_id, fav.content_type) in mapper
        ]

        return favorites_data

    async def remove_favorite(self, user_id: int, favorites_data: BaseModel) -> None:
        exists = await self.db.favorites.get_one_or_none(
            user_id=user_id, **favorites_data.model_dump()
        )
        if exists is None:
            raise FavoriteNotFoundException
        await self.db.favorites.delete(user_id=user_id, **favorites_data.model_dump())
        await self.db.commit()

    async def check_content_exists(self, content_id: int, content_type: str) -> bool:
        return await self.http_adapter.content_exists(content_id, content_type)
