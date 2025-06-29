from uuid import UUID

from fastapi import APIRouter, UploadFile, File

from src.enums import ContentType
from src.exceptions import (
    InvalidContentTypeException,
    InvalidImageTypeHTTPException,
)
from src.api.dependencies import ImageServiceDep


router = APIRouter(prefix="/images", tags=["Images"])


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
