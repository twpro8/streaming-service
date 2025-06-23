from typing import List
from uuid import UUID

from fastapi import APIRouter, UploadFile, File, Query

from src.core.enums import Qualities
from src.files.dependencies import FileServiceDep


router = APIRouter(tags=["Files"])


@router.post("/videos/{content_id}")
async def upload_video(
    file_service: FileServiceDep,
    content_id: UUID,
    qualities: List[Qualities] = Query(default=[Qualities.CD]),
    file: UploadFile = File(...),
):
    await file_service.upload_video(content_id=content_id, qualities=qualities, file=file)
    return {"status": "ok"}


@router.post("/images/{content_id}")
async def upload_image(
    file_service: FileServiceDep,
    content_id: UUID,
    file: UploadFile = File(...)
):
    await file_service.upload_image(content_id=content_id, file=file)
    return {"status": "ok"}


@router.delete("/videos/{content_id}", status_code=204)
async def delete_video(file_service: FileServiceDep, content_id: UUID):
    await file_service.delete_video(content_id=content_id)


@router.delete("/images/{content_id}", status_code=204)
async def delete_image(file_service: FileServiceDep, content_id: UUID):
    await file_service.delete_image(content_id=content_id)
