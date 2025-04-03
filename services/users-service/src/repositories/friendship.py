from sqlalchemy import insert
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
