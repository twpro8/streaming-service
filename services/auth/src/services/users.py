from src.schemas.users import UserWithFavoritesDTO
from src.services.base import BaseService


class UserService(BaseService):
    async def get_user(self, user_id: int):
        user = await self.db.users.get_one(id=user_id)
        favorites = await self.db.favorites.get_filtered(user_id=user_id)
        users_favorites = [favorite.id for favorite in favorites]
        user = UserWithFavoritesDTO(
            id=user.id,
            email=user.email,
            name=user.name,
            bio=user.bio,
            avatar=user.avatar,
            provider=user.provider,
            provider_id=user.provider_id,
            created_at=user.created_at,
            is_admin=user.is_admin,
            is_active=user.is_active,
            favorites_ids=users_favorites,
        )
        return user
