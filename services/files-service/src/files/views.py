from typing import List
from uuid import UUID

from fastapi import APIRouter, UploadFile, File, Query

from src.core.enums import Qualities
from src.files.service import FileService


router = APIRouter(tags=["Files"])


@router.post("/videos/{content_id}")
async def upload_video(
    content_id: UUID,
    qualities: List[Qualities] = Query(default=[Qualities.CD]),
    file: UploadFile = File(...),
):
    await FileService().upload_video(content_id=content_id, qualities=qualities, file=file)
    return {"status": "ok"}


@router.post("/images/{content_id}")
async def upload_image(content_id: UUID, file: UploadFile = File(...)):
    await FileService().upload_image(content_id=content_id, file=file)
    return {"status": "ok"}
