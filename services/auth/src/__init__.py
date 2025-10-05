from src.config import settings
from src.managers.redis import RedisManager
from src.adapters.aiohttp_client import AiohttpClient
from src.adapters.google_client import GoogleOAuthClient
from src.adapters.jwt_provider import JwtProvider
from src.adapters.password_hasher import PasswordHasher

redis_manager = RedisManager(url=settings.REDIS_URL)
aiohttp_client = AiohttpClient()
google_oauth_client = GoogleOAuthClient(
    ac=aiohttp_client,
    redis=redis_manager,
    client_id=settings.OAUTH_GOOGLE_CLIENT_ID,
    client_secret=settings.OAUTH_GOOGLE_CLIENT_SECRET,
    base_url=settings.OAUTH_GOOGLE_BASE_URL,
    redirect_uri=settings.OAUTH_GOOGLE_REDIRECT_URL,
    token_url=settings.GOOGLE_TOKEN_URL,
    jwks_url=settings.GOOGLE_JWKS_URL,
)
jwt_provider = JwtProvider(
    secret_key=settings.JWT_SECRET_KEY,
    algorithm=settings.JWT_ALGORITHM,
    access_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    refresh_expire_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
)
password_hasher = PasswordHasher(schemes=["bcrypt"], deprecated="auto")
