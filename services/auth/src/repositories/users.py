from src.repositories.base import BaseRepository
from src.models import UserORM
from src.repositories.mappers.mappers import UserDataMapper


class UserRepository(BaseRepository):
    model = UserORM
    mapper = UserDataMapper
