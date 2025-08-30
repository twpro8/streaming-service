from typing import List
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import insert, select, delete
from sqlalchemy.exc import IntegrityError

from src.exceptions import DirectorAlreadyExistsException, DirectorNotFoundException
from src.models import MovieDirectorORM, ShowDirectorORM
from src.models.directors import DirectorORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import (
    DirectorDataMapper,
    MovieDirectorDataMapper,
    ShowDirectorDataMapper,
)


class DirectorRepository(BaseRepository):
    model = DirectorORM
    mapper = DirectorDataMapper

    async def add_director(self, data: BaseModel) -> None:
        try:
            await self.add(data)
        except IntegrityError as e:
            raise DirectorAlreadyExistsException from e

    async def update_director(
        self,
        director_id: UUID,
        data: BaseModel,
        exclude_unset: bool = False,
    ) -> None:
        try:
            await self.update(id=director_id, data=data, exclude_unset=exclude_unset)
        except IntegrityError as e:
            raise DirectorAlreadyExistsException from e


class MovieDirectorRepository(BaseRepository):
    model = MovieDirectorORM
    mapper = MovieDirectorDataMapper

    async def add_movie_directors(self, data: List[BaseModel]):
        try:
            await self.add_bulk(data)
        except IntegrityError as exc:
            raise DirectorNotFoundException from exc

    async def update_movie_directors(self, movie_id: UUID, directors_ids: List[int]):
        query = select(self.model.director_id).filter_by(movie_id=movie_id)
        res = await self.session.execute(query)

        existed_ids = set(res.scalars().all())
        new_ids = set(directors_ids)

        to_add: set[int] = new_ids - existed_ids
        to_del: set[int] = existed_ids - new_ids

        if to_del:
            await self.session.execute(
                delete(self.model).filter(
                    self.model.movie_id == movie_id,
                    self.model.director_id.in_(to_del),
                )
            )
        if to_add:
            values = [
                {
                    "movie_id": movie_id,
                    "director_id": director_id,
                }
                for director_id in to_add
            ]
            try:
                await self.session.execute(insert(self.model).values(values))
            except IntegrityError as exc:
                raise DirectorNotFoundException from exc


class ShowDirectorRepository(BaseRepository):
    model = ShowDirectorORM
    mapper = ShowDirectorDataMapper

    async def add_show_directors(self, data: List[BaseModel]):
        try:
            await self.add_bulk(data)
        except IntegrityError as exc:
            raise DirectorNotFoundException from exc

    async def update_show_directors(self, show_id: UUID, directors_ids: List[int]):
        query = select(self.model.director_id).filter_by(show_id=show_id)
        res = await self.session.execute(query)

        existed_ids = set(res.scalars().all())
        new_ids = set(directors_ids)

        to_add: set[int] = new_ids - existed_ids
        to_del: set[int] = existed_ids - new_ids

        if to_del:
            await self.session.execute(
                delete(self.model).filter(
                    self.model.show_id == show_id,
                    self.model.director_id.in_(to_del),
                )
            )
        if to_add:
            values = [
                {
                    "show_id": show_id,
                    "director_id": director_id,
                }
                for director_id in to_add
            ]
            try:
                await self.session.execute(insert(self.model).values(values))
            except IntegrityError as exc:
                raise DirectorNotFoundException from exc
