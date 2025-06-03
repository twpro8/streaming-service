from src.files.service import FileService


class FileServiceFactory:
    @staticmethod
    async def file_service_factory() -> FileService:
        return FileService()
