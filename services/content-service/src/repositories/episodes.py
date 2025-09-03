import logging
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions import UniqueViolationError

from src.exceptions import EpisodeAlreadyExistsException, VideoUrlAlreadyExistsException
from src.repositories.base import BaseRepository
from src.models import EpisodeORM
from src.schemas.episodes import EpisodeDTO
from src.repositories.mappers.mappers import EpisodeDataMapper


log = logging.getLogger(__name__)


class EpisodeRepository(BaseRepository):
    model = EpisodeORM
    schema = EpisodeDTO
    mapper = EpisodeDataMapper

    async def get_episodes(
        self,
        show_id: UUID | None,
        season_id: int | None,
        episode_title: str | None,
        episode_number: int | None,
        limit: int,
        offset: int,
    ):
        query = select(EpisodeORM)
        if show_id is not None:
            query = query.filter_by(show_id=show_id)
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

    async def add_episode(self, data: BaseModel) -> None:
        try:
            await self.add(data)
        except IntegrityError as exc:
            if isinstance(exc.orig.__cause__, UniqueViolationError):
                cause = getattr(exc.orig, "__cause__", None)
                constraint = getattr(cause, "constraint_name", None)
                match constraint:
                    case "uq_episode":
                        raise EpisodeAlreadyExistsException
                    case "episodes_video_url_key":
                        raise VideoUrlAlreadyExistsException
                raise

    async def update_episode(
        self, data: BaseModel, exclude_unset: bool = False, **filter_by
    ) -> None:
        try:
            await self.update(data, exclude_unset=exclude_unset, **filter_by)
        except IntegrityError as exc:
            cause = getattr(exc.orig, "__cause__", None)
            constraint = getattr(cause, "constraint_name", None)
            if isinstance(cause, UniqueViolationError):
                match constraint:
                    case "uq_episode":
                        raise EpisodeAlreadyExistsException from exc
                    case "episodes_video_url_key":
                        raise VideoUrlAlreadyExistsException from exc
                raise
            else:
                log.exception(
                    f"Unknown error: failed to update data in database, input data: {data}"
                )
                raise
