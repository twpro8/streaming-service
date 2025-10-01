from src.models import UserORM
from src.repositories.mappers.base import DataMapper
from src.schemas.users import UserDTO


class UserDataMapper(DataMapper):
    db_model = UserORM
    schema = UserDTO
