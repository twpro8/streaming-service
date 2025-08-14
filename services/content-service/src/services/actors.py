from uuid import UUID

from src.exceptions import ActorAlreadyExistsException, ActorNotFoundException
from src.schemas.actors import ActorAddRequestDTO, ActorPatchDTO
from src.services.base import BaseService


class ActorService(BaseService):
    async def get_actors(self, page: int, per_page: int):
        return await self.db.actors.get_filtered(page=page, per_page=per_page)

    async def get_actor(self, actor_id: UUID):
        actor = await self.db.actors.get_one_or_none(id=actor_id)
        if actor is None:
            raise ActorNotFoundException
        return actor

    async def add_actor(self, actor_data: ActorAddRequestDTO):
        try:
            actor = await self.db.actors.add_actor(actor_data=actor_data)
        except ActorAlreadyExistsException:
            raise
        await self.db.commit()
        return actor

    async def update_actor(self, actor_id: UUID, actor_data: ActorPatchDTO):
        try:
            await self.db.actors.update_actor(
                actor_id=actor_id, actor_data=actor_data, exclude_unset=True
            )
        except ActorAlreadyExistsException:
            raise
        await self.db.commit()

    async def delete_actor(self, actor_id: UUID):
        await self.db.actors.delete(id=actor_id)
        await self.db.commit()
