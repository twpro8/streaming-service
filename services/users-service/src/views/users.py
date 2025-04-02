from fastapi import APIRouter

from src.services.users import UserService
from src.views.dependencies import DBDep, UserIdDep


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
async def get_me(db: DBDep, user_id: UserIdDep):
    user = await UserService(db).get_user(user_id=user_id)
    return {"status": "success", "user": user}
