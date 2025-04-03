from typing import List

from sqlalchemy import insert, delete, select
from sqlalchemy.exc import IntegrityError

from src.exceptions import ObjectAlreadyExistsException
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import FriendshipDataMapper

from src.models.users import FriendshipORM
from src.schemas.friendship import FriendshipDTO


class FriendshipRepository(BaseRepository):
    model = FriendshipORM
    schema = FriendshipDTO
    mapper = FriendshipDataMapper

    async def get_friends_ids(self, user_id: int) -> List[int]:
        query = select(FriendshipORM.friend_id).filter(FriendshipORM.user_id == user_id)
        friends1 = (await self.session.execute(query)).scalars().all()

        query = select(FriendshipORM.user_id).filter(FriendshipORM.friend_id == user_id)
        friends2 = (await self.session.execute(query)).scalars().all()

        return list(set(friends1 + friends2))

    async def add_friend(self, user_id: int, friend_id: int) -> None:
        stmt = insert(self.model).values(
            [
                {"user_id": user_id, "friend_id": friend_id},
                {"user_id": friend_id, "friend_id": user_id},
            ]
        )
        try:
            await self.session.execute(stmt)
        except IntegrityError:
            raise ObjectAlreadyExistsException

    async def remove_friend(self, user_id: int, friend_id: int) -> None:
        stmt = delete(FriendshipORM).filter(
            ((FriendshipORM.user_id == user_id) & (FriendshipORM.friend_id == friend_id))
            | ((FriendshipORM.user_id == friend_id) & (FriendshipORM.friend_id == user_id))
        )
        await self.session.execute(stmt)
