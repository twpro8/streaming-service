from src.repositories.base import BaseRepository
from src.models import RefreshTokenORM
from src.repositories.mappers.mappers import RefreshTokenDataMapper


class RefreshTokenRepository(BaseRepository):
    model = RefreshTokenORM
    mapper = RefreshTokenDataMapper
