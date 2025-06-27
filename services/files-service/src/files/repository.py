from src.core.base.repository import BaseRepository
from src.files.mapper import FileDataMapper
from src.files.models import FileORM
from src.files.schemas import FileDTO


class FileRepository(BaseRepository):
    model = FileORM
    schema = FileDTO
    mapper = FileDataMapper
