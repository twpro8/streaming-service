from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions import UniqueViolationError

from src.exceptions import (
    UniqueEpisodePerSeasonException,
    UniqueSeasonPerSeriesException,
    UniqueFileIDException,
)
from src.repositories.base import BaseRepository
from src.models.series import EpisodeORM
from src.schemas.episodes import EpisodeDTO
from src.repositories.mappers.mappers import EpisodeDataMapper


class EpisodeRepository(BaseRepository):
    model = EpisodeORM
    schema = EpisodeDTO
    mapper = EpisodeDataMapper

    async def get_episodes(
        self,
        series_id: int,
        season_id: int | None,
        episode_title: str | None,
        episode_number: int | None,
        offset: int,
        limit: int,
    ):
        query = select(EpisodeORM).filter_by(series_id=series_id)
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

    async def add_episode(self, episode_data: BaseModel):
        try:
            episode = await self.add(data=episode_data)
        except IntegrityError as e:
            if isinstance(e.orig.__cause__, UniqueViolationError):
                match getattr(e.orig.__cause__, "constraint_name", None):
                    case "unique_episode_per_season":
                        raise UniqueEpisodePerSeasonException
                    case "unique_season_per_series":
                        raise UniqueSeasonPerSeriesException
                    case "episodes_file_id_key":
                        raise UniqueFileIDException
            raise
        return episode

    async def update_episode(self, episode_id: int, episode_data: EpisodeDTO):
        try:
            await self.update(id=episode_id, data=episode_data)
        except IntegrityError as e:
            if isinstance(e.orig.__cause__, UniqueViolationError):
                match getattr(e.orig.__cause__, "constraint_name", None):
                    case "unique_episode_per_season":
                        raise UniqueEpisodePerSeasonException
                    case "unique_season_per_series":
                        raise UniqueSeasonPerSeriesException
                    case "episodes_file_id_key":
                        raise UniqueFileIDException
            raise
