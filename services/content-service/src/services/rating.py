from src.exceptions import ContentNotFoundException
from src.schemas.rating import RatingAddRequestDTO
from src.services.base import BaseService


class RatingService(BaseService):
    async def rate(self, user_id: int, data: RatingAddRequestDTO) -> None:
        if not await self.check_content_exists(data.content_id, data.content_type):
            raise ContentNotFoundException

        await self.db.rating.add_or_update_rating(
            user_id=user_id,
            content_id=data.content_id,
            content_type=data.content_type,
            value=data.value,
        )
        await self.db.commit()
