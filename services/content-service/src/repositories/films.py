import logging

from asyncpg import UniqueViolationError
from pydantic import BaseModel
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from src.exceptions import UniqueCoverURLException, UniqueVideoURLException
from src.models import FilmORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import FilmDataMapper
from src.repositories.utils import normalize_for_insert
from src.schemas.films import FilmDTO


log = logging.getLogger(__name__)


class FilmRepository(BaseRepository):
    model = FilmORM
    schema = FilmDTO
    mapper = FilmDataMapper

    async def update(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> None:
        data = normalize_for_insert(data.model_dump(exclude_unset=exclude_unset))
        stmt = update(self.model).values(**data).filter_by(**filter_by)
        try:
            await self.session.execute(stmt)
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
