from uuid import UUID

from sqlalchemy.exc import IntegrityError

from src.exceptions import ActorAlreadyExistsException
from src.models import ActorORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import ActorDataMapper
from src.schemas.actors import ActorDTO, ActorAddDTO, ActorPatchDTO


class ActorRepository(BaseRepository):
    model = ActorORM
    schema = ActorDTO
    mapper = ActorDataMapper

    async def add_actor(self, actor_data: ActorAddDTO):
        try:
            actor = await self.add(data=actor_data)
        except IntegrityError as exc:
            raise ActorAlreadyExistsException from exc
        return actor

    async def update_actor(
        self, actor_id: UUID, actor_data: ActorPatchDTO, exclude_unset: bool = False
    ):
        try:
            await self.update(id=actor_id, data=actor_data, exclude_unset=exclude_unset)
        except IntegrityError as exc:
            raise ActorAlreadyExistsException from exc
