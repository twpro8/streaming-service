from src.api.dependencies import (
    DBDep,
    RedisManagerDep,
    HTTPClientDep,
    GoogleOAuthClientDep,
    JwtProviderDep,
    PasswordHasherDep,
)
from src.services.auth import AuthService
from src.services.users import UserService


class ServiceFactory:
    @staticmethod
    def auth_service_factory(
        db: DBDep,
        redis_manager: RedisManagerDep,
        aiohttp_client: HTTPClientDep,
        google_oauth_client: GoogleOAuthClientDep,
        jwt_provider: JwtProviderDep,
        password_hasher: PasswordHasherDep,
    ) -> AuthService:
        return AuthService(
            db=db,
            redis=redis_manager,
            ac=aiohttp_client,
            google=google_oauth_client,
            jwt=jwt_provider,
            hasher=password_hasher,
        )

    @staticmethod
    def user_service_factory(db: DBDep) -> UserService:
        return UserService(db=db)
