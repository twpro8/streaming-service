import logging

from asyncpg import UniqueViolationError
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.exceptions import UniqueCoverURLException
from src.models import SeriesORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import SeriesDataMapper
from src.schemas.series import SeriesDTO


log = logging.getLogger(__name__)


class SeriesRepository(BaseRepository):
    model = SeriesORM
    schema = SeriesDTO
    mapper = SeriesDataMapper

    async def add_series(self, data: BaseModel):
        try:
            data = await self.add(data)
        except IntegrityError as exc:
            cause = getattr(exc.orig, "__cause__", None)
            constraint = getattr(cause, "constraint_name", None)
            if isinstance(cause, UniqueViolationError):
                match constraint:
                    case "series_cover_url_key":
                        raise UniqueCoverURLException from exc
            log.exception("Unknown error: failed to add data to database, input data: %s", data)
            raise
        return data

    async def update_series(
        self,
        data: BaseModel,
        exclude_unset: bool = False,
        **filter_by,
    ) -> None:
        try:
            await self.update(data, exclude_unset=exclude_unset, **filter_by)
        except IntegrityError as exc:
            cause = getattr(exc.orig, "__cause__", None)
            constraint = getattr(cause, "constraint_name", None)
            if isinstance(cause, UniqueViolationError):
                match constraint:
                    case "series_cover_url_key":
                        raise UniqueCoverURLException from exc
            log.exception("Unknown error: failed to update data in database, input data: %s", data)
            raise
