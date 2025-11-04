from src.repositories.base import BaseRepository
from src.models.rating import RatingORM, RatingAggregateORM
from src.repositories.mappers.mappers import RatingDataMapper, RatingAggregateDataMapper


class RatingRepository(BaseRepository):
    model = RatingORM
    mapper = RatingDataMapper


class RatingAggregateRepository(BaseRepository):
    model = RatingAggregateORM
    mapper = RatingAggregateDataMapper
