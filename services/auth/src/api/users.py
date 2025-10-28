from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import Response

from src.api.dependencies import UserIDDep
from src.factories.service import ServiceFactory
from src.schemas.users import UserPatchRequestDTO
from src.services.users import UserService


v1_router = APIRouter(prefix="/v1/users", tags=["Users"])


@v1_router.get("/me")
async def get_me(
    service: Annotated[UserService, Depends(ServiceFactory.user_service_factory)],
    user_id: UserIDDep,
):
    user = await service.get_user(user_id)
    return {"status": "ok", "data": user}


@v1_router.patch("")
async def update_user(
    service: Annotated[UserService, Depends(ServiceFactory.user_service_factory)],
    user_id: UserIDDep,
    user_data: UserPatchRequestDTO,
):
    await service.update_user(user_id, user_data)
    return {"status": "ok"}


@v1_router.delete("", status_code=204)
async def delete_user(
    service: Annotated[UserService, Depends(ServiceFactory.user_service_factory)],
    user_id: UserIDDep,
    response: Response,
):
    await service.delete_user(user_id)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
