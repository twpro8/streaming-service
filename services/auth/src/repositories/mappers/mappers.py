from src.models import UserORM, RefreshTokenORM
from src.repositories.mappers.base import DataMapper
from src.schemas.auth import RefreshTokenDTO
from src.schemas.users import UserDTO


class UserDataMapper(DataMapper):
    db_model = UserORM
    schema = UserDTO


class RefreshTokenDataMapper(DataMapper):
    db_model = RefreshTokenORM
    schema = RefreshTokenDTO
