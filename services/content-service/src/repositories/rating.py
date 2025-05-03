from decimal import Decimal

from sqlalchemy import select, func, update

from src.models import RatingORM, SeriesORM, FilmORM
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
        content_id: int,
        content_type: ContentType,
        value: Decimal
    ):
        # Checking an existing rating
        query = select(RatingORM).filter_by(
            user_id=user_id,
            content_id=content_id,
            content_type=content_type,
        )
        res = await self.session.execute(query)
        rating = res.scalars().one_or_none()

        if rating:
            old_rating = rating.rating
            rating.rating = value
            updated = old_rating != value  # Check if the rating changed
        else:
            self.session.add(RatingORM(
                user_id=user_id,
                content_id=content_id,
                content_type=content_type,
                rating=value
            ))
            updated = True

        await self.session.flush()

        # Calculating a new average
        avg_query = (
            select(func.avg(RatingORM.rating))
            .filter_by(
                content_id=content_id,
                content_type=content_type)
        )
        avg_res = await self.session.execute(avg_query)
        avg_rating = avg_res.scalar() or Decimal("0.0")

        # Updating the required table
        if updated:
            if content_type == ContentType.film:
                await self.session.execute(
                    update(FilmORM)
                    .filter_by(id=content_id)
                    .values(rating=avg_rating)
                )
            elif content_type == ContentType.series:
                await self.session.execute(
                    update(SeriesORM)
                    .filter_by(id=content_id)
                    .values(rating=avg_rating)
                )
