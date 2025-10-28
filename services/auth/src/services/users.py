from uuid import UUID

from src.schemas.users import UserPatchRequestDTO, UserPatchDTO
from src.services.base import BaseService


class UserService(BaseService):
    async def get_user(self, user_id: UUID):
        user = await self.db.users.get_one(id=user_id)
        return user

    async def update_user(self, user_id: UUID, user_data: UserPatchRequestDTO):
        _user_data = UserPatchDTO(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            birth_date=user_data.birth_date,
            bio=user_data.bio,
            picture=user_data.picture_str,
        )
        await self.db.users.update(id=user_id, data=_user_data, exclude_unset=True)
        await self.db.commit()

    async def delete_user(self, user_id: UUID):
        await self.db.users.delete(id=user_id)
        await self.db.commit()
