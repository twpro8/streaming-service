from src.core.base.mapper import DataMapper
from src.files.models import FileORM
from src.files.schemas import FileDTO


class FileDataMapper(DataMapper):
    db_model = FileORM
    schema = FileDTO
