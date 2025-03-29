from fastapi import APIRouter, Response, Request

from src.schemas.users import UserAddRequestDTO, UserLoginRequestDTO
from src.services.auth import AuthService
from src.views.dependencies import DBDep


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register(db: DBDep, user_data: UserAddRequestDTO):
    user = await AuthService(db).register_user(user_data)
    return {"status": "ok", "user": user}


@router.post("/login")
async def login_with_password(db: DBDep, user_data: UserLoginRequestDTO, response: Response):
    access_token = await AuthService(db).login_with_password(user_data)
    response.set_cookie("access_token", access_token, httponly=True)
    return {"status": "success", "access_token": access_token}


@router.get("/google-login", summary="Login or signup with google")
async def login_with_google(request: Request):
    return await AuthService.get_google_login_url(request)


@router.get("/google")
async def auth_google(db: DBDep, request: Request, response: Response):
    access_token = await AuthService(db).handle_google_callback(request)
    response.set_cookie("access_token", access_token, httponly=True)
    return {"status": "success", "access_token": access_token}
