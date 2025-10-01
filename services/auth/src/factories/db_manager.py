from src.db import session_maker
from src.managers.db import DBManager


class DBManagerFactory:
    @staticmethod
    def create():
        return DBManager(session_factory=session_maker)
