from fastapi import APIRouter, Response

from src.schemas.users import UserAddRequestDTO, UserLoginRequestDTO
from src.services.users import UserService
from src.views.dependencies import DBDep


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register(db: DBDep, user_data: UserAddRequestDTO):
    user = await UserService(db).register_user(user_data)
    return {"status": "ok", "user": user}


@router.post("/login")
async def login_with_password(db: DBDep, user_data: UserLoginRequestDTO, response: Response):
    access_token = await UserService(db).login_with_password(user_data)
    response.set_cookie("access_token", access_token, httponly=True)
    return {"status": "success", "access_token": access_token}
