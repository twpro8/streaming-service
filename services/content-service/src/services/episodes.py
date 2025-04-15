from src.services.base import BaseService
from src.schemas.episodes import EpisodeDTO
from src.exceptions import EpisodeNotFoundException


class EpisodeService(BaseService):
    """
    Service for managing episodes.
    """

    async def get_episodes_by_series_id(self, series_id: int):
        """
        Get all episodes by show ID.
        """
        return await self.db.episodes.get_filtered(series_id=series_id)

    async def get_episode_by_id(self, episode_id: int):
        """
        Get episode by ID.
        """
        episode = await self.db.episodes.get_one_or_none(id=episode_id)
        if not episode:
            raise EpisodeNotFoundException
        return episode

