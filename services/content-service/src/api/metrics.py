from fastapi import APIRouter, Response
from prometheus_client import generate_latest, REGISTRY


router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("")
async def metrics():
    return Response(generate_latest(REGISTRY), media_type="text/plain")
