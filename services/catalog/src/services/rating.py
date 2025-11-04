from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from src.enums import ContentType
from src.exceptions import ContentNotFoundException, SameRatingValueException
from src.schemas.rating import (
    RatingAddRequestDTO,
    RatingAddDTO,
    RatingAggregateDTO,
    RatingAggregateUpdateDTO,
    RatingUpdateDTO,
)
from src.services.base import BaseService


class RatingService(BaseService):
    async def rate(self, user_id: UUID, rating_data: RatingAddRequestDTO) -> None:
        # TODO: To apply cache.
        if not await self.check_content_exists(
            content_id=rating_data.content_id,
            content_type=rating_data.content_type,
        ):
            raise ContentNotFoundException

        delta_sum = rating_data.value
        delta_count = 1
        need_update = False

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
            _rating_data = RatingAddDTO(
                user_id=user_id,
                content_id=rating_data.content_id,
                value=rating_data.value,
            )
            await self.db.rating.add(_rating_data)

        # Updating aggregates
        # TODO: Use upsert to avoid blocking during high loads.
        aggregate = await self.db.rating_aggregates.get_one_or_none(
            content_id=rating_data.content_id,
            for_update=True,
        )

        if aggregate:
            new_sum = self._round(aggregate.rating_sum + delta_sum)
            new_count = aggregate.rating_count + delta_count
            new_avg = self._round(new_sum / new_count)

            if new_avg != aggregate.rating_avg:
                need_update = True

            await self.db.rating_aggregates.update(
                content_id=aggregate.content_id,
                data=RatingAggregateUpdateDTO(
                    rating_sum=new_sum,
                    rating_count=new_count,
                    rating_avg=new_avg,
                ),
            )
        else:
            await self.db.rating_aggregates.add(
                data=RatingAggregateDTO(
                    content_id=rating_data.content_id,
                    rating_sum=rating_data.value,
                    rating_count=1,
                    rating_avg=rating_data.value,
                )
            )
            new_avg = rating_data.value
            need_update = True

        # Updating the required table
        if need_update:
            if rating_data.content_type == ContentType.movie:
                await self.db.movies.update_rating(id=rating_data.content_id, value=new_avg)
            else:
                await self.db.shows.update_rating(id=rating_data.content_id, value=new_avg)

        await self.db.commit()

    @staticmethod
    def _round(value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
