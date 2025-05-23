from uuid import UUID

from pydantic import BaseModel

from src.applications.base import BaseAppService
from src.services.films import FilmService


class FilmAppService(BaseAppService):
    async def get_films(self):
        films = await FilmService(self.db).get_films()
        return films

    async def get_film(self, film_id: UUID):
        film = await FilmService(self.db).get_film(film_id=film_id)
        return film

    async def add_film(self, film_data: BaseModel):
        film = await FilmService(self.db).add_film(film_data=film_data)
        await self.publisher.publish_to_exchange(
            event="v1.film.created", message={"id": str(film.id)}
        )
        return film

    async def update_entire_film(self, film_id: UUID, film_data: BaseModel):
        await FilmService(self.db).update_entire_film(film_id=film_id, film_data=film_data)
        await self.publisher.publish_to_exchange(
            event="v1.film.replaced", message={"id": str(film_id)}
        )

    async def partly_update_film(self, film_id: UUID, film_data: BaseModel):
        await FilmService(self.db).partly_update_film(film_id=film_id, film_data=film_data)
        await self.publisher.publish_to_exchange(
            event="v1.film.updated", message={"id": str(film_id)}
        )

    async def remove_film(self, film_id: UUID):
        await FilmService(self.db).remove_film(film_id=film_id)
        await self.publisher.publish_to_exchange(
            event="v1.film.deleted", message={"id": str(film_id)}
        )
