from uuid import UUID

from fastapi import APIRouter, UploadFile, File

from src.enums import ContentType
from src.exceptions import (
    InvalidContentTypeException,
    InvalidImageTypeHTTPException,
    ImageNotFoundException,
    ImageNotFoundHTTPException,
)
from src.api.dependencies import ImageServiceDep, PaginationDep


router = APIRouter(prefix="/images", tags=["Images"])


@router.get("")
async def get_images_info_list(image_service: ImageServiceDep, pagination: PaginationDep):
    image_info_list = await image_service.get_images_info_list(pagination)
    return {"status": "ok", "data": image_info_list}


@router.get("/{content_id}")
async def get_image_info(image_service: ImageServiceDep, content_id: UUID):
    try:
        image_info = await image_service.get_image_info(content_id)
    except ImageNotFoundException:
        raise ImageNotFoundHTTPException
    return {"status": "ok", "data": image_info}


@router.post("/{content_id}")
async def upload_image(
    image_service: ImageServiceDep,
    content_id: UUID,
    content_type: ContentType,
    file: UploadFile = File(...),
):
    try:
        await image_service.upload_image(
            content_id=content_id,
            content_type=content_type,
            file=file,
        )
    except InvalidContentTypeException:
        raise InvalidImageTypeHTTPException
    return {"status": "ok"}


@router.delete("/{content_id}", status_code=204)
async def delete_image(
    image_service: ImageServiceDep,
    content_id: UUID,
):
    await image_service.delete_image(content_id=content_id)
