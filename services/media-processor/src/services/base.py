from src.utils.db_manager import DBManager
from src.interfaces.storage import AbstractStorage


class BaseService:
    db: DBManager = None
    storage: AbstractStorage = None

    def __init__(self, db: DBManager | None = None, storage: AbstractStorage | None = None) -> None:
        self.db = db
        self.storage = storage

    async def check_video_exists(self, **filter_by) -> bool:
        video = await self.db.videos.get_one_or_none(**filter_by)
        return video is not None
