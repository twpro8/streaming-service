from src.exceptions import (
    FriendshipAlreadyExistsException,
    UserNotFoundException,
    FriendshipNotFoundException,
    InvalidUsersDataException,
)
from src.services.base import BaseService


class FriendshipService(BaseService):
    async def get_friends(self, user_id: int):
        friends = await self.db.friendships.get_friends(user_id)
        return friends

    async def add_friend(self, user_id: int, friend_id: int) -> None:
        if user_id == friend_id:
            raise InvalidUsersDataException
        if await self.is_friend(user_id, friend_id):
            raise FriendshipAlreadyExistsException
        try:
            await self.db.friendships.add_friend(user_id=user_id, friend_id=friend_id)
        except UserNotFoundException:
            raise UserNotFoundException
        await self.db.commit()

    async def remove_friend(self, user_id: int, friend_id: int) -> None:
        if not await self.is_friend(user_id, friend_id):
            raise FriendshipNotFoundException

        await self.db.friendships.delete_friend(user_id=user_id, friend_id=friend_id)
        await self.db.commit()
