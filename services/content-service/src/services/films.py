from decimal import Decimal
from typing import List
from uuid import UUID


from src.enums import SortBy, SortOrder
from src.schemas.actors import FilmActorDTO
from src.schemas.films import FilmAddRequestDTO, FilmAddDTO, FilmPatchRequestDTO, FilmPatchDTO
from src.schemas.genres import FilmGenreDTO
from src.services.base import BaseService
from src.exceptions import (
    FilmNotFoundException,
    UniqueCoverURLException,
    UniqueVideoURLException,
    GenreNotFoundException,
    ActorNotFoundException,
)


class FilmService(BaseService):
    async def get_films(
        self,
        page: int | None,
        per_page: int | None,
        title: str | None,
        description: str | None,
        director: str | None,
        year: int | None,
        year_gt: int | None,
        year_lt: int | None,
        rating: Decimal | None,
        rating_ge: Decimal | None,
        rating_le: Decimal | None,
        genres_ids: List[int] | None,
        actors_ids: List[UUID] | None,
        sort_by: SortBy | None,
        sort_order: SortOrder | None,
    ):
        films = await self.db.films.get_filtered_films(
            page=page,
            per_page=per_page,
            title=title,
            description=description,
            director=director,
            year=year,
            year_gt=year_gt,
            year_lt=year_lt,
            rating=rating,
            rating_ge=rating_ge,
            rating_le=rating_le,
            genres_ids=genres_ids,
            actors_ids=actors_ids,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return films

    async def get_film(self, film_id: UUID):
        film = await self.db.films.get_one_or_none_with_rels(id=film_id)
        if film is None:
            raise FilmNotFoundException
        return film

    async def add_film(self, film_data: FilmAddRequestDTO):
        _film_data = FilmAddDTO(**film_data.model_dump())
        try:
            film = await self.db.films.add_film(_film_data)
        except UniqueCoverURLException:
            raise

        if film_data.genres_ids:
            _film_genres_data = [
                FilmGenreDTO(film_id=film.id, genre_id=genre_id)
                for genre_id in film_data.genres_ids
            ]
            try:
                await self.db.films_genres.add_film_genres(_film_genres_data)
            except GenreNotFoundException:
                raise
        if film_data.actors_ids:
            _film_actors_data = [
                FilmActorDTO(film_id=film.id, actor_id=actor_id)
                for actor_id in film_data.actors_ids
            ]
            try:
                await self.db.films_actors.add_film_actors(_film_actors_data)
            except ActorNotFoundException:
                raise

        await self.db.commit()
        return film

    async def update_film(self, film_id: UUID, film_data: FilmPatchRequestDTO):
        if not await self.check_film_exists(id=film_id):
            raise FilmNotFoundException

        _film_data = FilmPatchDTO(**film_data.model_dump(exclude_unset=True))

        try:
            await self.db.films.update_film(id=film_id, data=_film_data, exclude_unset=True)
        except UniqueCoverURLException:
            raise UniqueCoverURLException
        except UniqueVideoURLException:
            raise UniqueVideoURLException

        if film_data.genres_ids is not None:
            try:
                await self.db.films_genres.update_film_genres(
                    film_id=film_id,
                    genres_ids=film_data.genres_ids,
                )
            except GenreNotFoundException:
                raise
        if film_data.actors_ids is not None:
            try:
                await self.db.films_actors.update_film_actors(
                    film_id=film_id,
                    actors_ids=film_data.actors_ids,
                )
            except ActorNotFoundException:
                raise

        await self.db.commit()

    async def remove_film(self, film_id: UUID):
        await self.db.films.delete(id=film_id)
        await self.db.commit()
