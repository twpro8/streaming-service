from src.factories.repository import RepositoryFactory


class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.repos = None

    async def __aenter__(self):
        self.session = self.session_factory()
        self.repos = RepositoryFactory(self.session)
        return self

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    def __getattr__(self, name: str):
        return getattr(self.repos, name)
