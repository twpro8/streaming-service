from fastapi import APIRouter

from src.views.dependencies import DBDep


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register(db: DBDep): ...


@router.post("/login")
async def login_with_password(db: DBDep): ...
