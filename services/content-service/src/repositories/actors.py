from typing import List
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select, delete, insert
from sqlalchemy.exc import IntegrityError

from src.exceptions import ActorAlreadyExistsException, ActorNotFoundException
from src.models.actors import ActorORM, FilmActorORM, SeriesActorORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import (
    ActorDataMapper,
    FilmActorDataMapper,
    SeriesActorDataMapper,
)
from src.schemas.actors import (
    ActorDTO,
    ActorPatchDTO,
    FilmActorDTO,
    SeriesActorDTO,
    ActorAddDTO,
)


class ActorRepository(BaseRepository):
    model = ActorORM
    schema = ActorDTO
    mapper = ActorDataMapper

    async def add_actor(self, actor_data: ActorAddDTO) -> None:
        try:
            await self.add(data=actor_data)
        except IntegrityError as exc:
            raise ActorAlreadyExistsException from exc

    async def update_actor(
        self, actor_id: UUID, actor_data: ActorPatchDTO, exclude_unset: bool = False
    ):
        try:
            await self.update(id=actor_id, data=actor_data, exclude_unset=exclude_unset)
        except IntegrityError as exc:
            raise ActorAlreadyExistsException from exc


class FilmActorRepository(BaseRepository):
    model = FilmActorORM
    schema = FilmActorDTO
    mapper = FilmActorDataMapper

    async def add_film_actors(self, data: List[BaseModel]):
        try:
            await self.add_bulk(data)
        except IntegrityError as exc:
            raise ActorNotFoundException from exc

    async def update_film_actors(self, film_id: int, actors_ids: List[UUID]):
        query = select(self.model.actor_id).filter_by(film_id=film_id)
        res = await self.session.execute(query)

        existed_ids = set(res.scalars().all())
        new_ids = set(actors_ids)

        to_add: set[UUID] = new_ids - existed_ids
        to_del: set[UUID] = existed_ids - new_ids

        if to_del:
            await self.session.execute(
                delete(self.model).filter(
                    self.model.film_id == film_id,
                    self.model.actor_id.in_(to_del),
                )
            )
        if to_add:
            values = [{"film_id": film_id, "actor_id": actor_id} for actor_id in to_add]
            try:
                await self.session.execute(insert(self.model).values(values))
            except IntegrityError as exc:
                raise ActorNotFoundException from exc


class SeriesActorRepository(BaseRepository):
    model = SeriesActorORM
    schema = SeriesActorDTO
    mapper = SeriesActorDataMapper

    async def add_series_actors(self, data: List[BaseModel]):
        try:
            await self.add_bulk(data)
        except IntegrityError as exc:
            raise ActorNotFoundException from exc

    async def update_series_actors(self, series_id: int, actors_ids: List[UUID]):
        query = select(self.model.actor_id).filter_by(series_id=series_id)
        res = await self.session.execute(query)

        existed_ids = set(res.scalars().all())
        new_ids = set(actors_ids)

        to_add: set[UUID] = new_ids - existed_ids
        to_del: set[UUID] = existed_ids - new_ids

        if to_del:
            await self.session.execute(
                delete(self.model).filter(
                    self.model.series_id == series_id,
                    self.model.actor_id.in_(to_del),
                )
            )
        if to_add:
            values = [{"series_id": series_id, "actor_id": actor_id} for actor_id in to_add]
            try:
                await self.session.execute(insert(self.model).values(values))
            except IntegrityError as exc:
                raise ActorNotFoundException from exc
