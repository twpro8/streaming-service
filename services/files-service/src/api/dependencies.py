from typing import Annotated

from fastapi import Depends

from src.factories.services_factories import VideoServiceFactory, ImageServiceFactory
from src.services.images import ImageService
from src.services.videos import VideoService


VideoServiceDep = Annotated[VideoService, Depends(VideoServiceFactory.video_service_factory)]
ImageServiceDep = Annotated[ImageService, Depends(ImageServiceFactory.image_service_factory)]
