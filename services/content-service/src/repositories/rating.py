from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, update

from src.models import RatingORM, ShowORM, MovieORM, RatingAggregateORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import RatingDataMapper
from src.enums import ContentType


class RatingRepository(BaseRepository):
    model = RatingORM
    mapper = RatingDataMapper

    async def add_or_update_rating(
        self,
        user_id: UUID,
        content_id: UUID,
        content_type: ContentType,
        value: Decimal,
    ) -> None:
        delta_sum = value
        delta_count = 1
        need_update = False

        # checking an existing rating
        query = (
            select(RatingORM)
            .filter_by(
                user_id=user_id,
                content_id=content_id,
            )
            .with_for_update()
        )
        res = await self.session.execute(query)
        rating = res.scalar_one_or_none()

        if rating:
            if rating.value == value:  # checking if user rating has changed
                return
            delta_sum = value - rating.value
            delta_count = 0
            rating.value = value
        else:
            self.session.add(
                RatingORM(
                    user_id=user_id,
                    content_id=content_id,
                    value=value,
                )
            )

        # updating aggregates
        query = select(RatingAggregateORM).filter_by(content_id=content_id).with_for_update()
        res = await self.session.execute(query)
        aggregate = res.scalar_one_or_none()

        if aggregate:
            aggregate.rating_sum += delta_sum
            aggregate.rating_count += delta_count
            old_avg = aggregate.rating_avg
            new_avg = aggregate.rating_sum / aggregate.rating_count
            if new_avg != old_avg:
                aggregate.rating_avg = new_avg
                need_update = True
        else:
            self.session.add(
                RatingAggregateORM(
                    content_id=content_id,
                    rating_sum=value,
                    rating_count=1,
                    rating_avg=value,
                )
            )
            new_avg = value
            need_update = True

        await self.session.flush()

        # updating the required table
        if need_update:
            if content_type == ContentType.movie:
                await self.session.execute(
                    update(MovieORM).filter_by(id=content_id).values(rating=new_avg)
                )
            elif content_type == ContentType.show:
                await self.session.execute(
                    update(ShowORM).filter_by(id=content_id).values(rating=new_avg)
                )
