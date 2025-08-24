from uuid import UUID

from fastapi import APIRouter
from fastapi.params import Query

from src.exceptions import (
    ContentNotFoundHTTPException,
    ContentNotFoundException,
    CommentNotFoundException,
    CommentNotFoundHTTPException,
)
from src.schemas.comments import CommentAddRequestDTO, CommentPutRequestDTO
from src.schemas.pydantic_types import ContentType
from src.services.comments import CommentService
from src.api.dependencies import DBDep, UserDep, PaginationDep


v1_router = APIRouter(prefix="/v1/comments", tags=["Comments"])


@v1_router.get("")
async def get_comments(
    db: DBDep,
    pagination: PaginationDep,
    content_id: UUID = Query(),
    content_type: ContentType = Query(),
):
    comments = await CommentService(db).get_comments(
        content_id=content_id,
        content_type=content_type,
        page=pagination.page,
        per_page=pagination.per_page,
    )
    return {"status": "ok", "data": comments}


@v1_router.get("/user")
async def get_user_comments(db: DBDep, pagination: PaginationDep, user_id: UserDep):
    comments = await CommentService(db).get_user_comments(
        user_id=user_id,
        page=pagination.page,
        per_page=pagination.per_page,
    )
    return {"status": "ok", "data": comments}


@v1_router.get("/{comment_id}")
async def get_comment(db: DBDep, comment_id: UUID):
    try:
        comment = await CommentService(db).get_comment(comment_id=comment_id)
    except CommentNotFoundException:
        raise CommentNotFoundHTTPException
    return {"status": "ok", "data": comment}


@v1_router.post("", status_code=201)
async def add_comment(db: DBDep, user_id: UserDep, data: CommentAddRequestDTO):
    try:
        comment_id = await CommentService(db).add_comment(user_id=user_id, data=data)
    except ContentNotFoundException:
        raise ContentNotFoundHTTPException
    return {"status": "ok", "data": {"id": comment_id}}


@v1_router.put("/{comment_id}")
async def update_comment(
    db: DBDep,
    user_id: UserDep,
    comment_id: UUID,
    data: CommentPutRequestDTO,
):
    try:
        await CommentService(db).update_comment(
            user_id=user_id,
            comment_id=comment_id,
            data=data,
        )
    except CommentNotFoundException:
        raise CommentNotFoundHTTPException
    return {"status": "ok"}


@v1_router.delete("/{comment_id}", status_code=204)
async def delete_comment(db: DBDep, user_id: UserDep, comment_id: UUID):
    await CommentService(db).remove_comment(comment_id=comment_id, user_id=user_id)
