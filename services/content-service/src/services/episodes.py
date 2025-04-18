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
    EpisodeDoesNotExistException,
    UniqueEpisodePerSeasonException,
    UniqueSeasonPerSeriesException,
    UniqueFileIDException,
)


class EpisodeService(BaseService):
    """
    Service for managing episodes.
    """

    async def get_episodes(
        self,
        series_id: int,
        page: int,
        per_page: int,
        season_id: int | None,
        episode_title: str | None,
        episode_number: int | None,
    ):
        """
        Get episodes by series ID. And optional by season ID.
        """
        if not await self.check_series_exists(series_id):
            raise SeriesNotFoundException
        if season_id and not await self.check_season_exists(season_id):
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

    async def get_episode_by_id(self, episode_id: int):
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
        if not await self.check_series_exists(data.series_id):
            raise SeriesNotFoundException
        if not await self.check_season_exists(data.season_id):
            raise SeasonNotFoundException
        try:
            new_episode = await self.db.episodes.add_episode(data)
        except UniqueEpisodePerSeasonException:
            raise UniqueEpisodePerSeasonException
        except UniqueSeasonPerSeriesException:
            raise UniqueSeasonPerSeriesException
        except UniqueFileIDException:
            raise UniqueFileIDException
        await self.db.commit()
        return new_episode

    async def update_episode(self, episode_id: int, data: EpisodePatchRequestDTO):
        """
        Update episode by ID.
        """
        if not await self.check_episode_exists(episode_id):
            raise EpisodeNotFoundException
        if data.series_id and not await self.check_series_exists(data.series_id):
            raise SeriesNotFoundException
        if data.season_id and not await self.check_season_exists(data.season_id):
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

    async def delete_episode(self, episode_id: int, data: EpisodeDeleteRequestDTO):
        """
        Delete episode by ID.
        """
        if not await self.check_series_exists(data.series_id):
            raise SeriesNotFoundException
        if not await self.check_season_exists(data.season_id):
            raise SeasonNotFoundException
        if not await self.check_episode_exists(episode_id):
            raise EpisodeDoesNotExistException
        await self.db.episodes.delete(
            id=episode_id, series_id=data.series_id, season_id=data.season_id
        )
        await self.db.commit()
