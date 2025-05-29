from src.config import settings
from src.adapters.s3_adapter import S3Adapter
from src.adapters.redis_adapter import RedisAdapter

storage = S3Adapter(
    access_key=settings.S3_ACCESS_KEY,
    secret_key=settings.S3_SECRET_KEY,
    bucket_name=settings.S3_BUCKET_NAME,
    endpoint_url=settings.S3_ENDPOINT_URL,
)

redis_manager = RedisAdapter(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
)
