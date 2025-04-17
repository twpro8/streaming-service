from sqlalchemy import select, func

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
