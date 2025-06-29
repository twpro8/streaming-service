from src.db import session_maker
from src.utils.db_manager import DBManager


class DBManagerFactory:
    @staticmethod
    def db_manager_factory():
        return DBManager(session_factory=session_maker)

    @classmethod
    async def get_db(cls):
        async with cls.db_manager_factory() as db:
            yield db
