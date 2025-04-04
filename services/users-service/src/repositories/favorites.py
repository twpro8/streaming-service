from src.models import FavoritesORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import FavoritesDataMapper
from src.schemas.favorites import FavoriteDTO


class FavoritesRepository(BaseRepository):
    model = FavoritesORM
    schema = FavoriteDTO
    mapper = FavoritesDataMapper
