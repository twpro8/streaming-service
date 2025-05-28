from src.adapters.s3 import S3Adapter
from src.config import settings
from src.services.video import VideoService

storage = S3Adapter(
    access_key=settings.S3_ACCESS_KEY,
    secret_key=settings.S3_SECRET_KEY,
    bucket_name=settings.S3_BUCKET_NAME,
    endpoint_url=settings.S3_ENDPOINT_URL,
)
video_service = VideoService(storage=storage)
