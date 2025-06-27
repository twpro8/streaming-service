from uuid import UUID

from src.db import DBManager
from src.schemas.pydantic_types import ContentType


class BaseService:
    db: DBManager = None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    async def check_film_exists(self, film_id: UUID) -> bool:
        film = await self.db.films.get_one_or_none(id=film_id)
        return film is not None

    async def check_series_exists(self, series_id: UUID) -> bool:
        series = await self.db.series.get_one_or_none(id=series_id)
        return series is not None

    async def check_season_exists(self, season_id: UUID) -> bool:
        season = await self.db.seasons.get_one_or_none(id=season_id)
        return season is not None

    async def check_episode_exists(self, episode_id: UUID) -> bool:
        episode = await self.db.episodes.get_one_or_none(id=episode_id)
        return episode is not None

    async def check_comment_exists(self, **filter_by):
        comment = await self.db.comments.get_one_or_none(**filter_by)
        return comment is not None

    async def check_content_exists(self, content_id: UUID, content_type: ContentType) -> bool:
        exists = False

        if content_type == ContentType.film:
            exists |= await self.check_film_exists(content_id)
        if content_type == ContentType.series:
            exists |= await self.check_series_exists(content_id)

        return exists

    @staticmethod
    def get_content_type_key(content_type: ContentType):
        return "film_id" if content_type == ContentType.film else "series_id"
