from sqlalchemy.exc import IntegrityError

from src.exceptions import GenreAlreadyExistsException
from src.models import GenreORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import GenreDataMapper
from src.schemas.genres import GenreDTO, GenreAddDTO


class GenreRepository(BaseRepository):
    model = GenreORM
    schema = GenreDTO
    mapper = GenreDataMapper
