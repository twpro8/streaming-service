from uuid import UUID

from src.managers.db import DBManager
from src.enums import ContentType


class BaseService:
    db: DBManager = None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    async def check_movie_exists(self, **filter_by) -> bool:
        movie = await self.db.movies.get_one_or_none(**filter_by)
        return movie is not None

    async def check_show_exists(self, **filter_by) -> bool:
        show = await self.db.shows.get_one_or_none(**filter_by)
        return show is not None

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

        if content_type == ContentType.movie:
            exists |= await self.check_movie_exists(id=content_id)
        if content_type == ContentType.show:
            exists |= await self.check_show_exists(id=content_id)

        return exists

    async def check_director_exists(self, **filter_by) -> bool:
        director = await self.db.directors.get_one_or_none(**filter_by)
        return director is not None

    @staticmethod
    def get_content_type_key(content_type: ContentType):
        return "movie_id" if content_type == ContentType.movie else "show_id"
