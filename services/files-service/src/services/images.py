from uuid import UUID

from fastapi import UploadFile

from src.config import settings
from src.enums import ContentType
from src.exceptions import InvalidContentTypeException
from src.schemas.files import FileAddDTO
from src.services.base import BaseService
from src.services.utils import sanitize_filename


class ImageService(BaseService):
    async def upload_image(self, content_id: UUID, content_type: ContentType, file: UploadFile):
        if file.content_type not in settings.IMAGE_MIMO:
            raise InvalidContentTypeException

        storage_path = f"images/{content_id}.{file.content_type.split('/')[-1]}"
        original_filename = sanitize_filename(file.filename)

        await self.db.images.add(
            FileAddDTO(
                content_id=content_id,
                filename=original_filename,
                storage_path=storage_path,
                mime_type=file.content_type,
                size_in_bytes=file.size,
                content_type=content_type,
            )
        )
        await self.storage.upload_file(key=storage_path, data=file.file.read())
        await self.db.commit()

    async def delete_image(self, content_id: UUID):
        image_info = await self.db.images.get_one_or_none(content_id=content_id)
        if not image_info:
            return
        await self.storage.delete_file(key=image_info.storage_path)
        await self.db.images.delete(content_id=image_info.content_id)
        await self.db.commit()
