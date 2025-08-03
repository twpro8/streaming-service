from uuid import UUID

from src.exceptions import ContentNotFoundException, CommentNotFoundException
from src.schemas.comments import CommentAddRequestDTO, CommentAddDTO, CommentPutRequestDTO
from src.schemas.pydantic_types import ContentType
from src.services.base import BaseService


class CommentService(BaseService):
    async def get_comments(
        self,
        content_id: UUID,
        content_type: ContentType,
        page: int,
        per_page: int,
    ):
        key = self.get_content_type_key(content_type)
        comments = await self.db.comments.get_comments(
            **{key: content_id},
            limit=per_page,
            offset=per_page * (page - 1),
        )
        return comments

    async def get_user_comments(self, user_id: UUID, page: int, per_page: int):
        comments = await self.db.comments.get_comments(
            user_id=user_id,
            limit=per_page,
            offset=per_page * (page - 1),
        )
        return comments

    async def get_comment(self, comment_id: UUID):
        comment = await self.db.comments.get_one_or_none(id=comment_id)
        if not comment:
            raise CommentNotFoundException
        return comment

    async def add_comment(self, user_id: int, data: CommentAddRequestDTO):
        if not await self.check_content_exists(data.content_id, data.content_type):
            raise ContentNotFoundException

        key = self.get_content_type_key(data.content_type)
        new_comment = CommentAddDTO(user_id=user_id, **{key: data.content_id}, comment=data.comment)
        comment = await self.db.comments.add(data=new_comment)

        await self.db.commit()
        return comment

    async def update_comment(self, user_id: int, comment_id: UUID, data: CommentPutRequestDTO):
        if not await self.check_comment_exists(id=comment_id, user_id=user_id):
            raise CommentNotFoundException
        await self.db.comments.update(id=comment_id, user_id=user_id, data=data)
        await self.db.commit()

    async def remove_comment(self, comment_id: UUID, user_id: int):
        await self.db.comments.delete(id=comment_id, user_id=user_id)
        await self.db.commit()
