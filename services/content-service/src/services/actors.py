from uuid import UUID, uuid4

from src.exceptions import ActorAlreadyExistsException, ActorNotFoundException
from src.schemas.actors import ActorAddRequestDTO, ActorPatchDTO, ActorAddDTO
from src.services.base import BaseService


class ActorService(BaseService):
    async def get_actors(self, page: int, per_page: int):
        return await self.db.actors.get_filtered(page=page, per_page=per_page)

    async def get_actor(self, actor_id: UUID):
        actor = await self.db.actors.get_one_or_none(id=actor_id)
        if actor is None:
            raise ActorNotFoundException
        return actor

    async def add_actor(self, actor_data: ActorAddRequestDTO) -> UUID:
        actor_id = uuid4()
        _actor_data = ActorAddDTO(id=actor_id, **actor_data.model_dump())
        try:
            await self.db.actors.add_actor(actor_data=_actor_data)
        except ActorAlreadyExistsException:
            raise
        await self.db.commit()
        return actor_id

    async def update_actor(self, actor_id: UUID, actor_data: ActorPatchDTO):
        try:
            await self.db.actors.update_actor(
                actor_id=actor_id,
                actor_data=actor_data,
                exclude_unset=True,
            )
        except (ActorNotFoundException, ActorAlreadyExistsException):
            raise
        await self.db.commit()

    async def delete_actor(self, actor_id: UUID):
        await self.db.actors.delete(id=actor_id)
        await self.db.commit()
