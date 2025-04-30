from src.exceptions import CommentNotFoundException, ContentNotFoundException
from src.schemas.comments import CommentAddRequestDTO, CommentAddDTO
from src.schemas.pydantic_types import ContentType
from src.services.base import BaseService


class CommentService(BaseService):
    async def get_content_comments(self, content_id: int, content_type: ContentType):
        if not await self.check_content_exists(content_id, content_type):
            raise ContentNotFoundException

        key = self.get_content_type_key(content_type)
        comments = await self.db.comments.get_filtered(**{key: content_id})
        return comments

    async def add_comment(self, user_id: int, data: CommentAddRequestDTO):
        if not await self.check_content_exists(data.content_id, data.content_type):
            raise ContentNotFoundException

        key = self.get_content_type_key(data.content_type)
        new_comment = CommentAddDTO(user_id=user_id, **{key: data.content_id}, text=data.text)
        comment = await self.db.comments.add(data=new_comment)

        await self.db.commit()
        return comment

    async def remove_comment(self, user_id: int, comment_id: int):
        if not await self.check_comment_exists(id=comment_id):
            raise CommentNotFoundException

        await self.db.comments.delete(id=comment_id, user_id=user_id)
        await self.db.commit()
