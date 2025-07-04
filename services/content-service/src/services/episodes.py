from uuid import UUID

from src.schemas.episodes import (
    EpisodeDeleteRequestDTO,
    EpisodePatchRequestDTO,
    EpisodeAddDTO,
)
from src.services.base import BaseService
from src.exceptions import (
    EpisodeNotFoundException,
    SeriesNotFoundException,
    SeasonNotFoundException,
    UniqueEpisodePerSeasonException,
    UniqueSeasonPerSeriesException,
    UniqueFileIDException,
    ObjectAlreadyExistsException,
    EpisodeAlreadyExistsException,
)


class EpisodeService(BaseService):
    """
    Service for managing episodes.
    """

    async def get_episodes(
        self,
        series_id: UUID,
        season_id: UUID | None,
        page: int,
        per_page: int,
        episode_title: str | None,
        episode_number: int | None,
    ):
        """
        Get episodes by series ID. And optional by season ID.
        """
        if not await self.check_series_exists(id=series_id):
            raise SeriesNotFoundException
        if season_id and not await self.check_season_exists(id=season_id):
            raise SeasonNotFoundException
        episodes = await self.db.episodes.get_episodes(
            series_id=series_id,
            season_id=season_id,
            episode_title=episode_title,
            episode_number=episode_number,
            limit=per_page,
            offset=(page - 1) * per_page,
        )
        return episodes

    async def get_episode_by_id(self, episode_id: UUID):
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
            new_episode = await self.db.episodes.add_episode(data)
        except UniqueEpisodePerSeasonException:
            raise UniqueEpisodePerSeasonException
        except UniqueSeasonPerSeriesException:
            raise UniqueSeasonPerSeriesException
        except UniqueFileIDException:
            raise UniqueFileIDException
        except ObjectAlreadyExistsException:
            raise EpisodeAlreadyExistsException
        await self.db.commit()
        return new_episode

    async def update_episode(self, episode_id: UUID, data: EpisodePatchRequestDTO):
        """
        Update episode by ID.
        """
        if not await self.check_episode_exists(id=episode_id):
            raise EpisodeNotFoundException
        if data.series_id and not await self.check_series_exists(id=data.series_id):
            raise SeriesNotFoundException
        if data.season_id and not await self.check_season_exists(id=data.season_id):
            raise SeasonNotFoundException
        try:
            await self.db.episodes.update_episode(episode_id=episode_id, episode_data=data)
        except UniqueEpisodePerSeasonException:
            raise UniqueEpisodePerSeasonException
        except UniqueSeasonPerSeriesException:
            raise UniqueSeasonPerSeriesException
        except UniqueFileIDException:
            raise UniqueFileIDException
        await self.db.commit()

    async def delete_episode(self, data: EpisodeDeleteRequestDTO):
        """
        Delete episode by ID.
        """
        await self.db.episodes.delete(
            id=data.episode_id,
            season_id=data.season_id,
        )
        await self.db.commit()
