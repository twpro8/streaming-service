from src.models.images import ImageORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import ImageDataMapper
from src.schemas.files import FileDTO


class ImageRepository(BaseRepository):
    model = ImageORM
    schema = FileDTO
    mapper = ImageDataMapper
