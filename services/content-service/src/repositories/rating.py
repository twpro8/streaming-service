from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, update

from src.models import RatingORM, SeriesORM, FilmORM, RatingAggregateORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import RatingDataMapper
from src.schemas.pydantic_types import ContentType
from src.schemas.rating import RatingDTO


class RatingRepository(BaseRepository):
    model = RatingORM
    schema = RatingDTO
    mapper = RatingDataMapper

    async def add_or_update_rating(
        self,
        user_id: int,
        content_id: UUID,
        content_type: ContentType,
        value: Decimal,
    ):
        """
        Adds or updates a user's rating for a specific content (film or series) and updates the corresponding
        rating aggregates. If the rating is updated, the aggregate values (sum, count, average) are recalculated.
        The function also updates the average rating in the relevant content table (FilmORM or SeriesORM).

        Args:
            user_id (int): The ID of the user providing the rating.
            content_id (int): The ID of the content (film or series) being rated.
            content_type (ContentType): The type of content (film or series).
            value (Decimal): The rating value (between 0 and 10).

        Returns:
            None
        """

        delta_sum = value
        delta_count = 1

        # Checking an existing rating.
        rating = await self.get_one_or_none(user_id=user_id, content_id=content_id)

        if rating:
            if rating.rating == value:  # Checking if the average rating has changed.
                return
            delta_sum = value - rating.rating
            delta_count = 0
            rating.rating = value
        else:
            self.session.add(
                RatingORM(
                    user_id=user_id,
                    content_id=content_id,
                    rating=value,
                )
            )

        await self.session.flush()

        # Updating aggregates
        agg_query = select(RatingAggregateORM).filter_by(content_id=content_id)
        agg_res = await self.session.execute(agg_query)
        aggregate = agg_res.scalars().one_or_none()

        if aggregate:
            aggregate.rating_sum += delta_sum
            aggregate.rating_count += delta_count
            aggregate.rating_avg = aggregate.rating_sum / aggregate.rating_count
        else:
            self.session.add(
                RatingAggregateORM(
                    content_id=content_id,
                    rating_sum=value,
                    rating_count=1,
                    rating_avg=value,
                )
            )

        await self.session.flush()

        # Updating the required table
        if content_type == ContentType.film:
            await self.session.execute(
                update(FilmORM)
                .filter_by(id=content_id)
                .values(rating=aggregate.rating_avg if aggregate else value)
            )
        elif content_type == ContentType.series:
            await self.session.execute(
                update(SeriesORM)
                .filter_by(id=content_id)
                .values(rating=aggregate.rating_avg if aggregate else value)
            )
