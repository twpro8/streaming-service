from asyncpg import ForeignKeyViolationError
from sqlalchemy.exc import IntegrityError
from typing import List

from sqlalchemy import insert, delete, select

from src.exceptions import UserNotFoundException
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import FriendshipDataMapper, UserDataMapper

from src.models.users import FriendshipORM, UserORM
from src.schemas.friendship import FriendshipDTO
from src.schemas.users import UserDTO


class FriendshipRepository(BaseRepository):
    model = FriendshipORM
    schema = FriendshipDTO
    mapper = FriendshipDataMapper

    async def get_friends(self, user_id: int) -> List[UserDTO]:
        query = (
            select(UserORM)
            .join(FriendshipORM, UserORM.id == FriendshipORM.friend_id)
            .filter_by(user_id=user_id)
        )
        res = await self.session.execute(query)
        models = res.scalars().all()
        return [UserDataMapper.map_to_domain_entity(model) for model in models]

    async def add_friend(self, user_id: int, friend_id: int) -> None:
        stmt = insert(FriendshipORM).values(user_id=user_id, friend_id=friend_id)
        try:
            await self.session.execute(stmt)
        except IntegrityError as e:
            if isinstance(e.orig.__cause__, ForeignKeyViolationError):
                constraint_name = getattr(e.orig.__cause__, "constraint_name", None)
                match constraint_name:
                    case "friendships_friend_id_fkey":
                        raise UserNotFoundException

    async def delete_friend(self, user_id: int, friend_id: int) -> None:
        stmt = delete(FriendshipORM).filter_by(user_id=user_id, friend_id=friend_id)
        await self.session.execute(stmt)
