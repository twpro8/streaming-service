from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.repositories.base import BaseRepository
from src.models.rating import RatingORM, RatingAggregateORM
from src.repositories.mappers.mappers import RatingDataMapper, RatingAggregateDataMapper
from src.schemas.rating import RatingAggregateAddUpdateDTO


class RatingRepository(BaseRepository):
    model = RatingORM
    mapper = RatingDataMapper


class RatingAggregateRepository(BaseRepository):
    model = RatingAggregateORM
    mapper = RatingAggregateDataMapper

    async def add_or_update_aggregate(self, data: RatingAggregateAddUpdateDTO):
        stmt = (
            pg_insert(self.model)
            .values(
                content_id=data.content_id,
                rating_sum=data.delta_sum,
                rating_count=data.delta_count,
            )
            .on_conflict_do_update(
                index_elements=[self.model.content_id],
                set_={
                    "rating_sum": self.model.rating_sum + data.delta_sum,
                    "rating_count": self.model.rating_count + data.delta_count,
                },
            )
            .returning(self.model.rating_avg)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one()
