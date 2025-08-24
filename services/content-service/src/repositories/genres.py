from typing import List

from pydantic import BaseModel
from sqlalchemy import select, delete, insert
from sqlalchemy.exc import IntegrityError

from src.exceptions import GenreNotFoundException
from src.models import GenreORM, FilmGenreORM, SeriesGenreORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import (
    GenreDataMapper,
    FilmGenreDataMapper,
    SeriesGenreDataMapper,
)
from src.repositories.utils import normalize_for_insert
from src.schemas.genres import GenreDTO, FilmGenreDTO, SeriesGenreDTO


class GenreRepository(BaseRepository):
    model = GenreORM
    schema = GenreDTO
    mapper = GenreDataMapper

    async def add_genre(self, data: BaseModel) -> int:
        data = normalize_for_insert(data.model_dump())
        stmt = insert(self.model).values(**data).returning(self.model.id)
        res = await self.session.execute(stmt)
        return res.scalars().one()


class FilmGenreRepository(BaseRepository):
    model = FilmGenreORM
    schema = FilmGenreDTO
    mapper = FilmGenreDataMapper

    async def add_film_genres(self, data: List[BaseModel]):
        try:
            await self.add_bulk(data)
        except IntegrityError as exc:
            raise GenreNotFoundException from exc

    async def update_film_genres(self, film_id: int, genres_ids: List[int]):
        query = select(self.model.genre_id).filter_by(film_id=film_id)
        res = await self.session.execute(query)

        existed_ids = set(res.scalars().all())
        new_ids = set(genres_ids)

        to_add: set[int] = new_ids - existed_ids
        to_del: set[int] = existed_ids - new_ids

        if to_del:
            await self.session.execute(
                delete(self.model).filter(
                    self.model.film_id == film_id,
                    self.model.genre_id.in_(to_del),
                )
            )
        if to_add:
            values = [{"film_id": film_id, "genre_id": genre_id} for genre_id in to_add]
            try:
                await self.session.execute(insert(self.model).values(values))
            except IntegrityError as exc:
                raise GenreNotFoundException from exc


class SeriesGenreRepository(BaseRepository):
    model = SeriesGenreORM
    schema = SeriesGenreDTO
    mapper = SeriesGenreDataMapper

    async def add_series_genres(self, data: List[BaseModel]):
        try:
            await self.add_bulk(data)
        except IntegrityError as exc:
            raise GenreNotFoundException from exc

    async def update_series_genres(self, series_id: int, genres_ids: List[int]):
        query = select(self.model.genre_id).filter_by(series_id=series_id)
        res = await self.session.execute(query)

        existed_ids = set(res.scalars().all())
        new_ids = set(genres_ids)

        to_add: set[int] = new_ids - existed_ids
        to_del: set[int] = existed_ids - new_ids

        if to_del:
            await self.session.execute(
                delete(self.model).filter(
                    self.model.series_id == series_id,
                    self.model.genre_id.in_(to_del),
                )
            )
        if to_add:
            values = [{"series_id": series_id, "genre_id": genre_id} for genre_id in to_add]
            try:
                await self.session.execute(insert(self.model).values(values))
            except IntegrityError as exc:
                raise GenreNotFoundException from exc
