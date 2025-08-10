from typing import List

from src.exceptions import (
    ObjectNotFoundException,
    GenreNotFoundException,
    GenreAlreadyExistsException,
)
from src.schemas.genres import GenreDTO, GenreAddDTO
from src.services.base import BaseService


class GenreService(BaseService):
    async def get_genres(self, per_page: int, page: int) -> List[GenreDTO]:
        genres = await self.db.genres.get_filtered(per_page=per_page, page=page)
        return genres

    async def get_genre(self, genre_id: int) -> GenreDTO:
        try:
            genre = await self.db.genres.get_one(id=genre_id)
        except ObjectNotFoundException:
            raise GenreNotFoundException
        return genre

    async def add_genre(self, genre_data: GenreAddDTO) -> GenreDTO:
        if await self.check_genre_exists(name=genre_data.name):
            raise GenreAlreadyExistsException
        genre = await self.db.genres.add(data=genre_data)
        await self.db.commit()
        return genre

    async def delete_genre(self, genre_id: int):
        await self.db.genres.delete(id=genre_id)
        await self.db.commit()
