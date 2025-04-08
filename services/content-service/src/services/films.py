from typing import List

from src.schemas.films import FilmAddDTO
from src.services.base import BaseService


class FilmService(BaseService):
    async def get_films(self, films_ids: List[int | None] = None):
        if films_ids is not None:
            films = await self.db.films.get_objects_by_ids(films_ids)
            return films
        films = await self.db.films.get_filtered()
        return films

    async def get_film(self, film_id: int):
        film = await self.db.films.get_one(id=film_id)
        return film

    async def add_film(self, film_data: FilmAddDTO):
        film = await self.db.films.add_one(film_data)
        await self.db.commit()
        return film

    async def remove_film(self, film_id: int):
        await self.db.films.delete(id=film_id)
        await self.rabbit_adapter.send_message("film_delete", str(film_id))
        await self.db.commit()
