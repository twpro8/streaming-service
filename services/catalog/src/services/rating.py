from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from src.enums import ContentType
from src.exceptions import ContentNotFoundException, SameRatingValueException
from src.schemas.rating import (
    RatingAddRequestDTO,
    RatingAddDTO,
    RatingAggregateAddUpdateDTO,
    RatingUpdateDTO,
)
from src.services.base import BaseService


class RatingService(BaseService):
    async def rate(self, user_id: UUID, rating_data: RatingAddRequestDTO) -> None:
        # TODO: To apply cache.
        content = await self.get_content_or_none(
            content_id=rating_data.content_id,
            content_type=rating_data.content_type,
        )
        if not content:
            raise ContentNotFoundException

        delta_sum = rating_data.value
        delta_count = 1

        # Checking an existing rating
        rating = await self.db.rating.get_one_or_none(
            user_id=user_id,
            content_id=rating_data.content_id,
            for_update=True,
        )

        if rating:
            # Checking if user rating has changed
            if rating.value == rating_data.value:
                raise SameRatingValueException

            delta_sum = rating_data.value - rating.value
            delta_count = 0

            await self.db.rating.update(
                user_id=user_id,
                content_id=rating_data.content_id,
                data=RatingUpdateDTO(value=rating_data.value),
            )
        else:
            await self.db.rating.add(
                data=RatingAddDTO(
                    user_id=user_id,
                    content_id=rating_data.content_id,
                    value=rating_data.value,
                )
            )

        # Add or update aggregates
        new_avg = await self.db.rating_aggregates.add_or_update_aggregate(
            data=RatingAggregateAddUpdateDTO(
                content_id=rating_data.content_id,
                delta_sum=delta_sum,
                delta_count=delta_count,
            )
        )

        # Updating the required table
        if content.rating != new_avg:
            if rating_data.content_type == ContentType.movie:
                await self.db.movies.update_rating(id=rating_data.content_id, value=new_avg)
            else:
                await self.db.shows.update_rating(id=rating_data.content_id, value=new_avg)

        await self.db.commit()
