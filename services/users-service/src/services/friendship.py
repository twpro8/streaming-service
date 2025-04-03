from src.exceptions import (
    FriendshipAlreadyExistsException,
    UserNotFoundException,
    InvalidUsersDataException,
    FriendshipNotFoundException,
)
from src.services.base import BaseService


class FriendshipService(BaseService):
    async def get_friends(self, user_id: int):
        user_ids = await self.db.friendships.get_friends_ids(user_id)
        friends = await self.db.users.get_users_by_ids(user_ids)
        return friends

    async def add_friend(self, user_id: int, friend_id: int) -> None:
        if user_id == friend_id:
            raise InvalidUsersDataException

        friend_exists = await self.db.users.get_one_or_none(id=friend_id)
        if friend_exists is None:
            raise UserNotFoundException

        if await self.check_friendship(user_id, friend_id):
            raise FriendshipAlreadyExistsException

        await self.db.friendships.add_friend(user_id=user_id, friend_id=friend_id)
        await self.db.commit()

    async def remove_friend(self, user_id: int, friend_id: int) -> None:
        if user_id == friend_id:
            raise InvalidUsersDataException

        if not await self.check_friendship(user_id, friend_id):
            raise FriendshipNotFoundException

        await self.db.friendships.remove_friend(user_id, friend_id)
        await self.db.commit()

    async def check_friendship(self, user_id: int, friend_id: int) -> bool:
        friendship = await self.db.friendships.get_one_or_none(user_id=user_id, friend_id=friend_id)
        return True if friendship is not None else False
