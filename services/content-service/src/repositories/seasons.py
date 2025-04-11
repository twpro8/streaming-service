from src.models.series import SeasonORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import SeasonDataMapper
from src.schemas.seasons import SeasonDTO


class SeasonRepository(BaseRepository):
    model = SeasonORM
    schema = SeasonDTO
    mapper = SeasonDataMapper
