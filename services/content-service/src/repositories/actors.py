from typing import List
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select, delete, insert
from sqlalchemy.exc import IntegrityError

from src.exceptions import ActorAlreadyExistsException, ActorNotFoundException
from src.models.actors import ActorORM
from src.models.associations import MovieActorORM, ShowActorORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import (
    ActorDataMapper,
    MovieActorDataMapper,
    ShowActorDataMapper,
)
from src.schemas.actors import (
    ActorDTO,
    ActorPatchDTO,
    MovieActorDTO,
    ShowActorDTO,
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


class MovieActorRepository(BaseRepository):
    model = MovieActorORM
    schema = MovieActorDTO
    mapper = MovieActorDataMapper

    async def add_movie_actors(self, data: List[BaseModel]):
        try:
            await self.add_bulk(data)
        except IntegrityError as exc:
            raise ActorNotFoundException from exc

    async def update_movie_actors(self, movie_id: int, actors_ids: List[UUID]):
        query = select(self.model.actor_id).filter_by(movie_id=movie_id)
        res = await self.session.execute(query)

        existed_ids = set(res.scalars().all())
        new_ids = set(actors_ids)

        to_add: set[UUID] = new_ids - existed_ids
        to_del: set[UUID] = existed_ids - new_ids

        if to_del:
            await self.session.execute(
                delete(self.model).filter(
                    self.model.movie_id == movie_id,
                    self.model.actor_id.in_(to_del),
                )
            )
        if to_add:
            values = [{"movie_id": movie_id, "actor_id": actor_id} for actor_id in to_add]
            try:
                await self.session.execute(insert(self.model).values(values))
            except IntegrityError as exc:
                raise ActorNotFoundException from exc


class ShowActorRepository(BaseRepository):
    model = ShowActorORM
    schema = ShowActorDTO
    mapper = ShowActorDataMapper

    async def add_show_actors(self, data: List[BaseModel]):
        try:
            await self.add_bulk(data)
        except IntegrityError as exc:
            raise ActorNotFoundException from exc

    async def update_show_actors(self, show_id: int, actors_ids: List[UUID]):
        query = select(self.model.actor_id).filter_by(show_id=show_id)
        res = await self.session.execute(query)

        existed_ids = set(res.scalars().all())
        new_ids = set(actors_ids)

        to_add: set[UUID] = new_ids - existed_ids
        to_del: set[UUID] = existed_ids - new_ids

        if to_del:
            await self.session.execute(
                delete(self.model).filter(
                    self.model.show_id == show_id,
                    self.model.actor_id.in_(to_del),
                )
            )
        if to_add:
            values = [{"show_id": show_id, "actor_id": actor_id} for actor_id in to_add]
            try:
                await self.session.execute(insert(self.model).values(values))
            except IntegrityError as exc:
                raise ActorNotFoundException from exc
