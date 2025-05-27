from src.adapters.s3 import S3Client
from src.config import settings
from src.repositories.files import FilesRepository
from src.services.video import VideoService

s3_client = S3Client(
    access_key=settings.S3_ACCESS_KEY,
    secret_key=settings.S3_SECRET_KEY,
    bucket_name=settings.S3_BUCKET_NAME,
    endpoint_url=settings.S3_ENDPOINT_URL,
)
files_repo = FilesRepository(s3_client)
video_service = VideoService(files_repo)
