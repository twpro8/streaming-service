from src.schemas.rating import RatingAddRequestDTO
from src.services.base import BaseService


class RatingService(BaseService):
    async def rate(self, user_id: int, data: RatingAddRequestDTO):
        await self.db.rating.add_or_update_rating(
            user_id=user_id,
            content_id=data.content_id,
            content_type=data.content_type,
            value=data.rating,
        )
        await self.db.commit()
