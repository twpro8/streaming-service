from src.repositories.mappers.base import DataMapper
from src.schemas.files import FileDTO
from src.models import VideoORM, ImageORM


class VideoDataMapper(DataMapper):
    db_model = VideoORM
    schema = FileDTO


class ImageDataMapper(DataMapper):
    db_model = ImageORM
    schema = FileDTO
