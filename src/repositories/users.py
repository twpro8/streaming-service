from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from src.exceptions import ObjectNotFoundException
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import UserDataMapper, DBUserDataMapper

from src.models.users import UserORM
from src.schemas.users import UserDTO


class UsersRepository(BaseRepository):
    model = UserORM
    schema = UserDTO
    mapper = UserDataMapper

    async def get_db_user(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        res = await self.session.execute(query)
        try:
            model = res.scalar_one()
        except NoResultFound:
            raise ObjectNotFoundException
        return DBUserDataMapper.map_to_domain_entity(model)
