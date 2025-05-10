from fastapi import APIRouter, UploadFile, File

from src import s3_client
from src.schemas.pydantic_types import ContentType


router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/upload")
async def upload_file(content_id: int, content_type: ContentType, file: UploadFile = File(...)):
    file_data = await file.read()

    s3_key = await s3_client.upload_file(
        filename=file.filename,
        content_type=content_type,
        content_id=content_id,
        data=file_data,
    )
    url = await s3_client.generate_presigned_url(
        filename=file.filename,
        content_type=content_type,
        content_id=content_id,
    )

    return {
        "status": "ok",
        "data": {
            "url": url,
            "s3_key": s3_key,
            "original_filename": file.filename,
            "type": content_type,
        },
    }
