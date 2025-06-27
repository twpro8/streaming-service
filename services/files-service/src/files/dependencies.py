from typing import Annotated

from fastapi import Depends

from src.factories.file_service_factories import FileServiceFactory
from src.files.service import FileService


FileServiceDep = Annotated[FileService, Depends(FileServiceFactory.file_service_factory)]
