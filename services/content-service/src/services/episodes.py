from pydantic import BaseModel

from src.services.base import BaseService
from src.exceptions import EpisodeNotFoundException


class EpisodeService(BaseService):
    """
    Service for managing episodes.
    """

    async def get_episodes_by_series_id(self, series_id: int):
        """
        Get all episodes by show ID.
        """
        episodes = await self.db.episodes.get_filtered(series_id=series_id)
        return episodes

    async def get_episode_by_id(self, episode_id: int):
        """
        Get episode by ID.
        """
        episode = await self.db.episodes.get_one_or_none(id=episode_id)
        if not episode:
            raise EpisodeNotFoundException
        return episode

    async def add_episode(self, episode_data: BaseModel):
        """
        Add new episode.
        """
        new_episode = await self.db.episodes.add(episode_data)
        await self.db.commit()
        return new_episode

    async def update_episode(self, episode_id: int, episode_data: BaseModel):
        """
        Update episode by ID.
        """
        await self.db.episodes.update(id=episode_id, data=episode_data)
        await self.db.commit()

    async def delete_episode(self, episode_id: int):
        """
        Delete episode by ID.
        """
        await self.db.episodes.delete(id=episode_id)
        await self.db.commit()

