from uuid import UUID

from src.schemas.episodes import (
    EpisodePatchRequestDTO,
    EpisodeAddDTO,
)
from src.services.base import BaseService
from src.exceptions import (
    EpisodeNotFoundException,
    SeriesNotFoundException,
    SeasonNotFoundException,
    UniqueEpisodePerSeasonException,
    UniqueFileURLException,
)


class EpisodeService(BaseService):
    """
    Service for managing episodes.
    """

    async def get_episodes(
        self,
        series_id: UUID | None,
        season_id: UUID | None,
        title: str | None,
        episode_number: int | None,
        page: int,
        per_page: int,
    ):
        """
        Get episodes by series ID. And optional by season ID.
        """
        episodes = await self.db.episodes.get_episodes(
            series_id=series_id,
            season_id=season_id,
            episode_title=title,
            episode_number=episode_number,
            limit=per_page,
            offset=per_page * (page - 1),
        )
        return episodes

    async def get_episode(self, episode_id: UUID):
        """
        Get episode by ID.
        """
        episode = await self.db.episodes.get_one_or_none(id=episode_id)
        if not episode:
            raise EpisodeNotFoundException
        return episode

    async def add_episode(self, data: EpisodeAddDTO):
        """
        Add new episode.
        """
        if not await self.check_series_exists(id=data.series_id):
            raise SeriesNotFoundException
        if not await self.check_season_exists(id=data.season_id):
            raise SeasonNotFoundException
        try:
            new_episode = await self.db.episodes.add(data)
        except UniqueEpisodePerSeasonException:
            raise UniqueEpisodePerSeasonException
        except UniqueFileURLException:
            raise UniqueFileURLException
        await self.db.commit()
        return new_episode

    async def update_episode(self, episode_id: UUID, data: EpisodePatchRequestDTO):
        """
        Update episode by ID.
        """
        if not await self.check_episode_exists(id=episode_id):
            raise EpisodeNotFoundException
        try:
            await self.db.episodes.update(id=episode_id, data=data, exclude_unset=True)
        except UniqueEpisodePerSeasonException:
            raise UniqueEpisodePerSeasonException
        await self.db.commit()

    async def delete_episode(self, episode_id: UUID):
        """
        Delete episode by ID.
        """
        await self.db.episodes.delete(id=episode_id)
        await self.db.commit()
