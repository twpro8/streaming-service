from typing import List
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select, insert, delete
from sqlalchemy.exc import IntegrityError

from src.exceptions import CountryAlreadyExistsException, CountryNotFoundException
from src.models import CountryORM, MovieCountryORM, ShowCountryORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import (
    CountryDataMapper,
    ShowCountryDataMapper,
    MovieCountryDataMapper,
)


class CountryRepository(BaseRepository):
    model = CountryORM
    mapper = CountryDataMapper

    async def add_country(self, data: BaseModel) -> int:
        stmt = insert(self.model).values(**data.model_dump()).returning(self.model.id)
        try:
            res = await self.session.execute(stmt)
        except IntegrityError as e:
            raise CountryAlreadyExistsException from e
        return res.scalars().one()

    async def update_country(
        self,
        country_id: int,
        data: BaseModel,
        exclude_unset: bool = False,
    ):
        try:
            await self.update(id=country_id, data=data, exclude_unset=exclude_unset)
        except IntegrityError as e:
            raise CountryAlreadyExistsException from e


class MovieCountryRepository(BaseRepository):
    model = MovieCountryORM
    mapper = MovieCountryDataMapper

    async def add_movie_countries(self, data: List[BaseModel]):
        try:
            await self.add_bulk(data)
        except IntegrityError as exc:
            raise CountryNotFoundException from exc

    async def update_movie_countries(self, movie_id: UUID, countries_ids: List[int]):
        query = select(self.model.country_id).filter_by(movie_id=movie_id)
        res = await self.session.execute(query)

        existed_ids = set(res.scalars().all())
        new_ids = set(countries_ids)

        to_add: set[int] = new_ids - existed_ids
        to_del: set[int] = existed_ids - new_ids

        if to_del:
            await self.session.execute(
                delete(self.model).filter(
                    self.model.movie_id == movie_id,
                    self.model.country_id.in_(to_del),
                )
            )
        if to_add:
            values = [
                {
                    "movie_id": movie_id,
                    "country_id": country_id,
                }
                for country_id in to_add
            ]
            try:
                await self.session.execute(insert(self.model).values(values))
            except IntegrityError as exc:
                raise CountryNotFoundException from exc


class ShowCountryRepository(BaseRepository):
    model = ShowCountryORM
    mapper = ShowCountryDataMapper

    async def add_show_countries(self, data: List[BaseModel]):
        try:
            await self.add_bulk(data)
        except IntegrityError as exc:
            raise CountryNotFoundException from exc

    async def update_show_countries(self, show_id: UUID, countries_ids: List[int]):
        query = select(self.model.country_id).filter_by(show_id=show_id)
        res = await self.session.execute(query)

        existed_ids = set(res.scalars().all())
        new_ids = set(countries_ids)

        to_add: set[int] = new_ids - existed_ids
        to_del: set[int] = existed_ids - new_ids

        if to_del:
            await self.session.execute(
                delete(self.model).filter(
                    self.model.show_id == show_id,
                    self.model.country_id.in_(to_del),
                )
            )
        if to_add:
            values = [
                {
                    "show_id": show_id,
                    "country_id": country_id,
                }
                for country_id in to_add
            ]
            try:
                await self.session.execute(insert(self.model).values(values))
            except IntegrityError as exc:
                raise CountryNotFoundException from exc
