from uuid import UUID

from src.db import DBManager
from src.schemas.pydantic_types import ContentType


class BaseService:
    db: DBManager = None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    async def check_film_exists(self, **filter_by) -> bool:
        film = await self.db.films.get_one_or_none(**filter_by)
        return film is not None

    async def check_series_exists(self, **filter_by) -> bool:
        series = await self.db.series.get_one_or_none(**filter_by)
        return series is not None

    async def check_season_exists(self, **filter_by) -> bool:
        season = await self.db.seasons.get_one_or_none(**filter_by)
        return season is not None

    async def check_episode_exists(self, **filter_by) -> bool:
        episode = await self.db.episodes.get_one_or_none(**filter_by)
        return episode is not None

    async def check_comment_exists(self, **filter_by) -> bool:
        comment = await self.db.comments.get_one_or_none(**filter_by)
        return comment is not None

    async def check_genre_exists(self, **filter_by) -> bool:
        genre = await self.db.genres.get_one_or_none(**filter_by)
        return genre is not None

    async def check_content_exists(self, content_id: UUID, content_type: ContentType) -> bool:
        exists = False

        if content_type == ContentType.film:
            exists |= await self.check_film_exists(id=content_id)
        if content_type == ContentType.series:
            exists |= await self.check_series_exists(id=content_id)

        return exists

    @staticmethod
    def get_content_type_key(content_type: ContentType):
        return "film_id" if content_type == ContentType.film else "series_id"
