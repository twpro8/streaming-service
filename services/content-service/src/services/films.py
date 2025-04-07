from typing import List

from src.connectors.rabbit_conn import RabbitManager
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

        rabbit = RabbitManager()
        await rabbit.connect()
        await rabbit.publish("film_delete", "%s" % film_id)
        await rabbit.close()

        await self.db.commit()
