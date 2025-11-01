from uuid import UUID

from uuid_extensions import uuid7

from src.schemas.episodes import (
    EpisodePatchRequestDTO,
    EpisodeAddDTO,
    EpisodeAddRequestDTO,
    EpisodePatchDTO,
)
from src.services.base import BaseService
from src.exceptions import (
    EpisodeNotFoundException,
    ShowNotFoundException,
    SeasonNotFoundException,
    EpisodeAlreadyExistsException,
    NotFoundException,
    VideoUrlAlreadyExistsException,
)


class EpisodeService(BaseService):
    """
    Service for managing episodes.
    """

    async def get_episodes(
        self,
        show_id: UUID | None,
        season_id: UUID | None,
        episode_number: int | None,
        page: int,
        per_page: int,
    ):
        """
        Get episodes by show ID. And optional by season ID.
        """
        episodes = await self.db.episodes.get_episodes(
            show_id=show_id,
            season_id=season_id,
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

    async def add_episode(self, episode_data: EpisodeAddRequestDTO) -> UUID:
        """
        Add new episode.
        """
        if not await self.check_show_exists(id=episode_data.show_id):
            raise ShowNotFoundException
        if not await self.check_season_exists(
            id=episode_data.season_id,
            show_id=episode_data.show_id,
        ):
            raise SeasonNotFoundException

        episode_id = uuid7()
        _episode_data = EpisodeAddDTO(id=episode_id, **episode_data.model_dump())

        try:
            await self.db.episodes.add_episode(_episode_data)
        except (EpisodeAlreadyExistsException, VideoUrlAlreadyExistsException):
            raise

        await self.db.commit()
        return episode_id

    async def update_episode(self, episode_id: UUID, episode_data: EpisodePatchRequestDTO):
        """
        Update episode by ID.
        """
        _episode_data = EpisodePatchDTO(**episode_data.model_dump(exclude_unset=True))
        try:
            await self.db.episodes.update_episode(
                id=episode_id,
                data=_episode_data,
                exclude_unset=True,
            )
        except NotFoundException:
            raise EpisodeNotFoundException
        except (EpisodeAlreadyExistsException, VideoUrlAlreadyExistsException):
            raise
        await self.db.commit()

    async def delete_episode(self, episode_id: UUID):
        """
        Delete episode by ID.
        """
        await self.db.episodes.delete(id=episode_id)
        await self.db.commit()
