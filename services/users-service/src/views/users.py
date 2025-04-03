from fastapi import APIRouter

from src.exceptions import (
    FriendshipAlreadyExistsException,
    FriendshipAlreadyExistsHTTPException,
    UserNotFoundException,
    UserNotFoundHTTPException,
    InvalidUsersDataException,
    InvalidFriendIdException,
)
from src.services.friendship import FriendshipService
from src.services.users import UserService
from src.views.dependencies import DBDep, UserIdDep


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/{user_id}/friends/{friend_id}")
async def add_friend(db: DBDep, user_id: UserIdDep, friend_id: int):
    try:
        await FriendshipService(db).add_friend(user_id, friend_id)
    except FriendshipAlreadyExistsException:
        raise FriendshipAlreadyExistsHTTPException
    except UserNotFoundException:
        raise UserNotFoundHTTPException
    except InvalidUsersDataException:
        raise InvalidFriendIdException
    return {"status": "success"}


@router.get("")
async def get_me(db: DBDep, user_id: UserIdDep):
    user = await UserService(db).get_user(user_id=user_id)
    return {"status": "success", "user": user}
