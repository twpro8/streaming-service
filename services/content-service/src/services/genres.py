from typing import List

from pydantic import BaseModel

from src.exceptions import (
    ObjectNotFoundException,
    GenreNotFoundException,
    GenreAlreadyExistsException,
)
from src.schemas.genres import GenreAddDTO
from src.services.base import BaseService


class GenreService(BaseService):
    async def get_genres(self, per_page: int, page: int) -> List[BaseModel]:
        genres = await self.db.genres.get_filtered(per_page=per_page, page=page)
        return genres

    async def get_genre(self, genre_id: int) -> BaseModel:
        try:
            genre = await self.db.genres.get_one(id=genre_id)
        except ObjectNotFoundException:
            raise GenreNotFoundException
        return genre

    async def add_genre(self, genre_data: GenreAddDTO) -> int:
        if await self.check_genre_exists(name=genre_data.name):
            raise GenreAlreadyExistsException

        genre_id = await self.db.genres.add_genre(data=genre_data)

        await self.db.commit()
        return genre_id

    async def delete_genre(self, genre_id: int):
        await self.db.genres.delete(id=genre_id)
        await self.db.commit()
