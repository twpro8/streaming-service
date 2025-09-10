from typing import List
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select, delete, insert
from sqlalchemy.exc import IntegrityError

from src.exceptions import GenreNotFoundException
from src.models import GenreORM, MovieGenreORM, ShowGenreORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import (
    GenreDataMapper,
    MovieGenreDataMapper,
    ShowGenreDataMapper,
)


class GenreRepository(BaseRepository):
    model = GenreORM
    mapper = GenreDataMapper

    async def add_genre(self, data: BaseModel) -> int:
        stmt = insert(self.model).values(**data.model_dump()).returning(self.model.id)
        res = await self.session.execute(stmt)
        return res.scalars().one()


class MovieGenreRepository(BaseRepository):
    model = MovieGenreORM
    mapper = MovieGenreDataMapper

    async def add_movie_genres(self, data: List[BaseModel]):
        try:
            await self.add_bulk(data)
        except IntegrityError as e:
            raise GenreNotFoundException from e

    async def update_movie_genres(self, movie_id: UUID, genres_ids: List[int]):
        query = select(self.model.genre_id).filter_by(movie_id=movie_id)
        res = await self.session.execute(query)

        existed_ids = set(res.scalars().all())
        new_ids = set(genres_ids)

        to_add: set[int] = new_ids - existed_ids
        to_del: set[int] = existed_ids - new_ids

        if to_del:
            await self.session.execute(
                delete(self.model).filter(
                    self.model.movie_id == movie_id,
                    self.model.genre_id.in_(to_del),
                )
            )
        if to_add:
            values = [{"movie_id": movie_id, "genre_id": genre_id} for genre_id in to_add]
            try:
                await self.session.execute(insert(self.model).values(values))
            except IntegrityError as e:
                raise GenreNotFoundException from e


class ShowGenreRepository(BaseRepository):
    model = ShowGenreORM
    mapper = ShowGenreDataMapper

    async def add_show_genres(self, data: List[BaseModel]):
        try:
            await self.add_bulk(data)
        except IntegrityError as e:
            raise GenreNotFoundException from e

    async def update_show_genres(self, show_id: UUID, genres_ids: List[int]):
        query = select(self.model.genre_id).filter_by(show_id=show_id)
        res = await self.session.execute(query)

        existed_ids = set(res.scalars().all())
        new_ids = set(genres_ids)

        to_add: set[int] = new_ids - existed_ids
        to_del: set[int] = existed_ids - new_ids

        if to_del:
            await self.session.execute(
                delete(self.model).filter(
                    self.model.show_id == show_id,
                    self.model.genre_id.in_(to_del),
                )
            )
        if to_add:
            values = [{"show_id": show_id, "genre_id": genre_id} for genre_id in to_add]
            try:
                await self.session.execute(insert(self.model).values(values))
            except IntegrityError as e:
                raise GenreNotFoundException from e
