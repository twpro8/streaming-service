from fastapi import APIRouter

from src.views.dependencies import AdminDep


router = APIRouter(prefix="/episodes", tags=["Episodes"])


@router.get("")
async def get_episodes():
    return {"status": "ok", "data": []}


@router.post("", dependencies=[AdminDep])
async def add_new_episode():
    return {"status": "ok", "data": {}}


@router.patch("/{episode_id}", dependencies=[AdminDep])
async def update_episode(episode_id: int):
    return {"status": "ok", "data": {}}


@router.delete("/{episode_id}", dependencies=[AdminDep])
async def delete_episode(episode_id: int):
    return {"status": "ok"}

