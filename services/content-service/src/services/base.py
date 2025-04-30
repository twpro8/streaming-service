from src.db import DBManager


class BaseService:
    db: DBManager = None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    async def check_film_exists(self, film_id: int) -> bool:
        film = await self.db.films.get_one_or_none(id=film_id)
        return film is not None

    async def check_series_exists(self, series_id: int) -> bool:
        series = await self.db.series.get_one_or_none(id=series_id)
        return series is not None

    async def check_season_exists(self, season_id: int) -> bool:
        season = await self.db.seasons.get_one_or_none(id=season_id)
        return season is not None

    async def check_episode_exists(self, episode_id: int) -> bool:
        episode = await self.db.episodes.get_one_or_none(id=episode_id)
        return episode is not None
