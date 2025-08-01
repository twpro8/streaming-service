import logging

from asyncpg import UniqueViolationError
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.exceptions import UniqueCoverURLException, UniqueVideoURLException
from src.models import FilmORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import FilmDataMapper
from src.schemas.films import FilmDTO


log = logging.getLogger(__name__)


class FilmRepository(BaseRepository):
    model = FilmORM
    schema = FilmDTO
    mapper = FilmDataMapper

    async def add_film(self, data: BaseModel):
        try:
            data = await self.add(data)
        except IntegrityError as exc:
            cause = getattr(exc.orig, "__cause__", None)
            constraint = getattr(cause, "constraint_name", None)
            if isinstance(cause, UniqueViolationError):
                match constraint:
                    case "films_cover_url_key":
                        raise UniqueCoverURLException from exc
            log.exception("Unknown error: failed to add data to database, input data: %s", data)
            raise
        return data

    async def update_film(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> None:
        try:
            await self.update(data, exclude_unset=exclude_unset, **filter_by)
        except IntegrityError as exc:
            cause = getattr(exc.orig, "__cause__", None)
            constraint = getattr(cause, "constraint_name", None)
            if isinstance(cause, UniqueViolationError):
                match constraint:
                    case "films_cover_url_key":
                        raise UniqueCoverURLException from exc
                    case "films_video_url_key":
                        raise UniqueVideoURLException from exc
            log.exception("Unknown error: failed to update data in database, input data: %s", data)
            raise
