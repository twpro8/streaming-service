from src.models import UserORM, RefreshTokenORM
from src.repositories.mappers.base import DataMapper
from src.schemas.auth import RefreshTokenDTO
from src.schemas.users import UserDTO, DBUserDTO


class UserDataMapper(DataMapper):
    db_model = UserORM
    schema = UserDTO


class DBUserDataMapper(DataMapper):
    db_model = UserORM
    schema = DBUserDTO


class RefreshTokenDataMapper(DataMapper):
    db_model = RefreshTokenORM
    schema = RefreshTokenDTO
