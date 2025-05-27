from typing import Annotated

from fastapi import Depends

from src.services.video import VideoService
from src import video_service


def get_video_service() -> VideoService:
    return video_service


VideoServiceDep = Annotated[VideoService, Depends(get_video_service)]
