from src.models import SeriesORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import SeriesDataMapper
from src.schemas.series import SeriesDTO


class SeriesRepository(BaseRepository):
    model = SeriesORM
    schema = SeriesDTO
    mapper = SeriesDataMapper
