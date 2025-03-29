from pydantic import BaseModel

from src.exceptions import IncorrectPasswordException, UserNotFoundException
from src.schemas.users import UserAddDTO
from src.services.base import BaseService
from src.services.auth import AuthService


class UserService(BaseService):
    async def register_user(self, user_data: BaseModel):
        normalized_email = user_data.email.strip().lower()
        hashed_password = AuthService.get_password_hash(password=user_data.password)

        new_user_data = UserAddDTO(
            name=user_data.name, email=normalized_email, hashed_password=hashed_password
        )

        user = await self.db.users.add_one(new_user_data)
        await self.db.commit()
        return user

    async def login_with_password(self, user_data: BaseModel):
        user = await self.db.users.get_db_user(email=user_data.email)
        if not user:
            raise UserNotFoundException
        if not AuthService.verify_password(user_data.password, user.hashed_password):
            raise IncorrectPasswordException
        access_token = AuthService.create_access_token(
            {
                "user_id": user.id,
                "email": user.email,
                "name": user.name,
                "bio": user.bio,
                "avatar": user.avatar,
                "provider": user.provider,
                "created_at": str(user.created_at),
            }
        )
        return access_token
