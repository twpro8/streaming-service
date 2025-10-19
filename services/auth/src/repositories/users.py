from sqlalchemy import select
from sqlalchemy.testing.pickleable import User

from src.exceptions import UserNotFoundException
from src.repositories.base import BaseRepository
from src.models import UserORM
from src.repositories.mappers.mappers import UserDataMapper, DBUserDataMapper


class UserRepository(BaseRepository):
    model = UserORM
    mapper = UserDataMapper

    async def get_db_user(self, **filter_by) -> User:
        query = select(UserORM).filter_by(**filter_by)
        res = await self.session.execute(query)
        model = res.scalars().one_or_none()
        if model is None:
            raise UserNotFoundException
        return DBUserDataMapper.map_to_domain_entity(model)
