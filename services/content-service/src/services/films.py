from src.schemas.films import FilmAddDTO
from src.services.base import BaseService


class FilmService(BaseService):
    async def get_films(self):
        films = await self.db.films.get_filtered()
        return films

    async def get_film(self, film_id: int):
        film = await self.db.films.get_one(id=film_id)
        return film

    async def add_film(self, film_data: FilmAddDTO):
        film = await self.db.films.add_one(film_data)
        await self.db.commit()
        return film
