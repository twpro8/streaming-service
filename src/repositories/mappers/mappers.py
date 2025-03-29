from src.repositories.mappers.base import DataMapper
from src.models.users import UserORM
from src.schemas.users import UserDTO, DBUserDTO


class UserDataMapper(DataMapper):
    db_model = UserORM
    schema = UserDTO


class DBUserDataMapper(DataMapper):
    db_model = UserORM
    schema = DBUserDTO
