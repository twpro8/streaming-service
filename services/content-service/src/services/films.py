from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from src.schemas.films import FilmAddRequestDTO, FilmAddDTO
from src.schemas.genres import FilmGenreDTO
from src.services.base import BaseService
from src.exceptions import (
    ObjectNotFoundException,
    FilmNotFoundException,
    UniqueCoverURLException,
    UniqueVideoURLException,
    GenreNotFoundException,
)


class FilmService(BaseService):
    async def get_films(
        self,
        page: int,
        per_page: int,
        title: str | None,
        description: str | None,
        director: str | None,
        release_year: date | None,
        release_year_ge: date | None,
        release_year_le: date | None,
        rating: Decimal | None,
        rating_ge: Decimal | None,
        rating_le: Decimal | None,
    ):
        films = await self.db.films.get_filtered_films_or_series(
            page=page,
            per_page=per_page,
            title=title,
            description=description,
            director=director,
            release_year=release_year,
            release_year_ge=release_year_ge,
            release_year_le=release_year_le,
            rating=rating,
            rating_ge=rating_ge,
            rating_le=rating_le,
        )
        return films

    async def get_film(self, film_id: UUID):
        try:
            film = await self.db.films.get_one(id=film_id)
        except ObjectNotFoundException:
            raise FilmNotFoundException
        return film

    async def add_film(self, film_data: FilmAddRequestDTO):
        _film_data = FilmAddDTO(
            title=film_data.title,
            description=film_data.description,
            director=film_data.director,
            release_year=film_data.release_year,
            duration=film_data.duration,
            cover_url=film_data.cover_url,
        )
        try:
            film = await self.db.films.add_film(_film_data)
        except UniqueCoverURLException:
            raise

        if film_data.genres:
            _film_genres_data = [
                FilmGenreDTO(film_id=film.id, genre_id=genre_id) for genre_id in film_data.genres
            ]
            try:
                await self.db.films_genres.add_film_genres(_film_genres_data)
            except GenreNotFoundException:
                raise
        await self.db.commit()
        return film

    async def update_film(self, film_id: UUID, film_data: BaseModel):
        if not await self.check_film_exists(id=film_id):
            raise FilmNotFoundException
        try:
            await self.db.films.update_film(id=film_id, data=film_data, exclude_unset=True)
        except UniqueCoverURLException:
            raise UniqueCoverURLException
        except UniqueVideoURLException:
            raise UniqueVideoURLException
        await self.db.commit()

    async def remove_film(self, film_id: UUID):
        await self.db.films.delete(id=film_id)
        await self.db.commit()
