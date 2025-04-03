from src.exceptions import (
    FriendshipAlreadyExistsException,
    UserNotFoundException,
    InvalidUsersDataException,
)
from src.services.base import BaseService


class FriendshipService(BaseService):
    async def add_friend(self, user_id: int, friend_id: int) -> None:
        if user_id == friend_id:
            raise InvalidUsersDataException

        friend_exists = await self.db.users.get_one_or_none(id=friend_id)
        if friend_exists is None:
            raise UserNotFoundException

        friendship_exists = await self.db.friendships.get_one_or_none(
            user_id=user_id, friend_id=friend_id
        )
        if friendship_exists is not None:
            raise FriendshipAlreadyExistsException

        await self.db.friendships.add_friend(user_id=user_id, friend_id=friend_id)
        await self.db.commit()
