from src.api.dependencies import DBDep, RedisManagerDep, HTTPClientDep
from src.services.auth import AuthService
from src.services.users import UserService


class ServiceFactory:
    @staticmethod
    def auth_service_factory(
        db: DBDep,
        redis_manager: RedisManagerDep,
        aiohttp_client: HTTPClientDep,
    ) -> AuthService:
        return AuthService(db=db, redis=redis_manager, ac=aiohttp_client)

    @staticmethod
    def user_service_factory(db: DBDep) -> UserService:
        return UserService(db=db)
