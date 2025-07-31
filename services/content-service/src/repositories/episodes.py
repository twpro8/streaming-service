import logging

from pydantic import BaseModel
from sqlalchemy import select, func, update, insert
from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions import UniqueViolationError

from src.exceptions import (
    UniqueEpisodePerSeasonException,
    UniqueSeasonPerSeriesException,
    UniqueFileURLException,
)
from src.repositories.base import BaseRepository
from src.models.series import EpisodeORM
from src.repositories.utils import normalize_for_insert
from src.schemas.episodes import EpisodeDTO
from src.repositories.mappers.mappers import EpisodeDataMapper


log = logging.getLogger(__name__)


class EpisodeRepository(BaseRepository):
    model = EpisodeORM
    schema = EpisodeDTO
    mapper = EpisodeDataMapper

    async def get_episodes(
        self,
        series_id: int | None,
        season_id: int | None,
        episode_title: str | None,
        episode_number: int | None,
        limit: int,
        offset: int,
    ):
        query = select(EpisodeORM)
        if series_id is not None:
            query = query.filter_by(series_id=series_id)
        if season_id is not None:
            query = query.filter_by(season_id=season_id)
        if episode_title is not None:
            query = query.filter(
                func.lower(EpisodeORM.title).contains(episode_title.strip().lower())
            )
        if episode_number is not None:
            query = query.filter_by(episode_number=episode_number)
        query = query.offset(offset).limit(limit)
        res = await self.session.execute(query)
        episodes = res.scalars().all()
        return [EpisodeDataMapper.map_to_domain_entity(ep) for ep in episodes]

    async def add(self, data: BaseModel):
        data = normalize_for_insert(data.model_dump())
        stmt = insert(self.model).values(**data).returning(self.model)
        try:
            res = await self.session.execute(stmt)
        except IntegrityError as exc:
            if isinstance(exc.orig.__cause__, UniqueViolationError):
                cause = getattr(exc.orig, "__cause__", None)
                constraint = getattr(cause, "constraint_name", None)
                match constraint:
                    case "unique_episode_per_season":
                        raise UniqueEpisodePerSeasonException
                    case "unique_season_per_series":
                        raise UniqueSeasonPerSeriesException
                    case "episodes_video_url_key":
                        raise UniqueFileURLException
                raise
            raise
        model = res.scalars().one()
        return self.mapper.map_to_domain_entity(model)

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
                    case "unique_episode_per_season":
                        raise UniqueEpisodePerSeasonException from exc
                    case "episodes_video_url_key":
                        raise UniqueFileURLException from exc
                raise
            else:
                log.exception(
                    f"Unknown error: failed to update data in database, input data: {data}"
                )
                raise
