from src.models.videos import VideoORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import VideoDataMapper
from src.schemas.files import FileDTO


class VideoRepository(BaseRepository):
    model = VideoORM
    schema = FileDTO
    mapper = VideoDataMapper
