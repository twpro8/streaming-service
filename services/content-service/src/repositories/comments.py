from sqlalchemy import select

from src.models import CommentORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import CommentDataMapper
from src.schemas.comments import CommentDTO


class CommentRepository(BaseRepository):
    model = CommentORM
    schema = CommentDTO
    mapper = CommentDataMapper

    async def get_comments(self, offset: int, limit: int, **filter_by):
        query = (
            select(self.model)
            .filter_by(**filter_by)
            .order_by(self.model.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        res = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(model) for model in res.scalars().all()]
