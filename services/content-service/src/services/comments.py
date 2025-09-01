from uuid import UUID, uuid4

from src.exceptions import ContentNotFoundException, CommentNotFoundException
from src.schemas.comments import CommentAddRequestDTO, CommentAddDTO, CommentPutRequestDTO
from src.enums import ContentType
from src.services.base import BaseService


class CommentService(BaseService):
    async def get_comments(
        self,
        content_id: UUID,
        content_type: ContentType,
        page: int,
        per_page: int,
    ):
        comments = await self.db.comments.get_comments(
            content_id=content_id,
            content_type=content_type,
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

    async def add_comment(self, user_id: UUID, comment_data: CommentAddRequestDTO) -> UUID:
        if not await self.check_content_exists(
            content_id=comment_data.content_id,
            content_type=comment_data.content_type,
        ):
            raise ContentNotFoundException

        comment_id = uuid4()
        _new_data = CommentAddDTO(
            id=comment_id,
            user_id=user_id,
            **comment_data.model_dump(),
        )
        await self.db.comments.add(data=_new_data)

        await self.db.commit()
        return comment_id

    async def update_comment(
        self,
        user_id: UUID,
        comment_id: UUID,
        comment_data: CommentPutRequestDTO,
    ):
        if not await self.check_comment_exists(id=comment_id, user_id=user_id):
            raise CommentNotFoundException

        await self.db.comments.update(id=comment_id, user_id=user_id, data=comment_data)
        await self.db.commit()

    async def delete_comment(self, comment_id: UUID, user_id: UUID):
        await self.db.comments.delete(id=comment_id, user_id=user_id)
        await self.db.commit()
