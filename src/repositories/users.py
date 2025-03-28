from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import UserDataMapper

from src.models.users import UserORM
from src.schemas.users import UserDTO


class UsersRepository(BaseRepository):
    model = UserORM
    schema = UserDTO
    mapper = UserDataMapper
