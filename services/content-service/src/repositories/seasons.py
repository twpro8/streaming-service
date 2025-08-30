import logging
from uuid import UUID

from asyncpg import UniqueViolationError
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.exceptions import UniqueSeasonPerShowException
from src.models import SeasonORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import SeasonDataMapper
from src.schemas.seasons import SeasonDTO


log = logging.getLogger(__name__)


class SeasonRepository(BaseRepository):
    model = SeasonORM
    schema = SeasonDTO
    mapper = SeasonDataMapper

    async def add_season(self, data: BaseModel) -> None:
        try:
            await self.add(data)
        except IntegrityError as exc:
            cause = getattr(exc.orig, "__cause__", None)
            constraint = getattr(cause, "constraint_name", None)
            if isinstance(cause, UniqueViolationError):
                match constraint:
                    case "uq_season":
                        raise UniqueSeasonPerShowException from exc
            log.exception("Unknown error: failed to add data to database, input data: %s", data)
            raise

    async def update_season(self, season_id: UUID, data: BaseModel, exclude_unset: bool = False):
        try:
            data = await self.update(id=season_id, data=data, exclude_unset=exclude_unset)
        except IntegrityError as exc:
            cause = getattr(exc.orig, "__cause__", None)
            constraint = getattr(cause, "constraint_name", None)
            if isinstance(cause, UniqueViolationError):
                match constraint:
                    case "uq_season":
                        raise UniqueSeasonPerShowException from exc
            log.exception("Unknown error: failed to add data to database, input data: %s", data)
            raise
        return data
