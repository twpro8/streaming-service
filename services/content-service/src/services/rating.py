from uuid import UUID

from src.exceptions import ContentNotFoundException
from src.schemas.rating import RatingAddRequestDTO
from src.services.base import BaseService


class RatingService(BaseService):
    async def rate(self, user_id: UUID, data: RatingAddRequestDTO) -> None:
        if not await self.check_content_exists(data.content_id, data.content_type):
            raise ContentNotFoundException

        await self.db.rating.add_or_update_rating(user_id=user_id, **data.model_dump())
        await self.db.commit()
