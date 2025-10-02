from fastapi import APIRouter


v1_router = APIRouter(prefix="/v1/auth", tags=["auth"])


@v1_router.post("/refresh")
async def refresh_token(token: str): ...


@v1_router.post("/revoke")
async def revoke_token(token: str): ...
