from uuid import UUID

from pydantic import BaseModel

from src.services.base import BaseService


class FilmService(BaseService):
    async def get_films(self):
        films = await self.db.films.get_filtered()
        return films

    async def get_film(self, film_id: UUID):
        film = await self.db.films.get_one(id=film_id)
        return film

    async def add_film(self, film_data: BaseModel):
        film = await self.db.films.add(film_data)
        await self.db.commit()
        return film

    async def update_entire_film(self, film_id: UUID, film_data: BaseModel):
        await self.db.films.update(id=film_id, data=film_data)
        await self.db.commit()

    async def partly_update_film(self, film_id: UUID, film_data: BaseModel):
        await self.db.films.update(id=film_id, data=film_data, exclude_unset=True)
        await self.db.commit()

    async def remove_film(self, film_id: UUID):
        await self.db.films.delete(id=film_id)
        await self.db.commit()
