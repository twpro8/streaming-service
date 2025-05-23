from fastapi import APIRouter

from src.exceptions import (
    CommentNotFoundException,
    NoContentHTTPException,
    ContentNotFoundHTTPException,
    ContentNotFoundException,
)
from src.schemas.comments import CommentAddRequestDTO
from src.schemas.pydantic_types import ContentType
from src.services.comments import CommentService
from src.views.dependencies import DBDep, UserDep


router = APIRouter(tags=["Comments"])


@router.get("/content/{content_type}/{content_id}/comments")
async def get_comments(db: DBDep, content_type: ContentType, content_id: int):
    try:
        comments = await CommentService(db).get_content_comments(
            content_id=content_id, content_type=content_type
        )
    except ContentNotFoundException:
        raise ContentNotFoundHTTPException
    return {"status": "ok", "data": comments}


@router.post("/comments")
async def add_comment(db: DBDep, user_id: UserDep, data: CommentAddRequestDTO):
    try:
        comment = await CommentService(db).add_comment(user_id=user_id, data=data)
    except ContentNotFoundException:
        raise ContentNotFoundHTTPException
    return {"status": "ok", "data": comment}


@router.delete("/comments/{comment_id}")
async def delete_comment(db: DBDep, user_id: UserDep, comment_id: int):
    try:
        await CommentService(db).remove_comment(comment_id=comment_id, user_id=user_id)
    except CommentNotFoundException:
        raise NoContentHTTPException
    return {"status": "ok"}
