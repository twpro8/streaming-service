from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.params import Query

from src.exceptions import (
    ContentNotFoundHTTPException,
    ContentNotFoundException,
    CommentNotFoundException,
    CommentNotFoundHTTPException,
)
from src.factories.service import ServiceFactory
from src.schemas.comments import CommentAddRequestDTO, CommentPutRequestDTO
from src.enums import ContentType
from src.services.comments import CommentService
from src.api.dependencies import UserIDDep, PaginationDep


v1_router = APIRouter(prefix="/v1/comments", tags=["comments"])


@v1_router.get("")
async def get_comments(
    service: Annotated[CommentService, Depends(ServiceFactory.comment_service_factory)],
    pagination: PaginationDep,
    content_id: UUID = Query(),
    content_type: ContentType = Query(),
):
    comments = await service.get_comments(
        content_id=content_id,
        content_type=content_type,
        page=pagination.page,
        per_page=pagination.per_page,
    )
    return {"status": "ok", "data": comments}


@v1_router.get("/user")
async def get_user_comments(
    service: Annotated[CommentService, Depends(ServiceFactory.comment_service_factory)],
    pagination: PaginationDep,
    user_id: UserIDDep,
):
    comments = await service.get_user_comments(
        user_id=user_id,
        page=pagination.page,
        per_page=pagination.per_page,
    )
    return {"status": "ok", "data": comments}


@v1_router.get("/{comment_id}")
async def get_comment(
    service: Annotated[CommentService, Depends(ServiceFactory.comment_service_factory)],
    comment_id: UUID,
):
    try:
        comment = await service.get_comment(comment_id=comment_id)
    except CommentNotFoundException:
        raise CommentNotFoundHTTPException
    return {"status": "ok", "data": comment}


@v1_router.post("", status_code=201)
async def add_comment(
    service: Annotated[CommentService, Depends(ServiceFactory.comment_service_factory)],
    user_id: UserIDDep,
    comment_data: CommentAddRequestDTO,
):
    try:
        comment_id = await service.add_comment(user_id=user_id, comment_data=comment_data)
    except ContentNotFoundException:
        raise ContentNotFoundHTTPException
    return {"status": "ok", "data": {"id": comment_id}}


@v1_router.put("/{comment_id}")
async def update_comment(
    service: Annotated[CommentService, Depends(ServiceFactory.comment_service_factory)],
    user_id: UserIDDep,
    comment_id: UUID,
    comment_data: CommentPutRequestDTO,
):
    try:
        await service.update_comment(
            user_id=user_id,
            comment_id=comment_id,
            comment_data=comment_data,
        )
    except CommentNotFoundException:
        raise CommentNotFoundHTTPException
    return {"status": "ok"}


@v1_router.delete("/{comment_id}", status_code=204)
async def delete_comment(
    service: Annotated[CommentService, Depends(ServiceFactory.comment_service_factory)],
    user_id: UserIDDep,
    comment_id: UUID,
):
    await service.delete_comment(comment_id=comment_id, user_id=user_id)
