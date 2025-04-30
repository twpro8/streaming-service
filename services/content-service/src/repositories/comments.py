from src.models import CommentORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import CommentDataMapper
from src.schemas.comments import CommentDTO


class CommentRepository(BaseRepository):
    model = CommentORM
    schema = CommentDTO
    mapper = CommentDataMapper
