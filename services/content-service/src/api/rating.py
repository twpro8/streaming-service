from typing import Annotated

from fastapi import APIRouter, Depends

from src.exceptions import ContentNotFoundException, ContentNotFoundHTTPException
from src.factories.service import ServiceFactory
from src.schemas.rating import RatingAddRequestDTO
from src.services.rating import RatingService
from src.api.dependencies import UserIDDep


v1_router = APIRouter(prefix="/v1/ratings", tags=["ratings"])


@v1_router.post("")
async def rate_content(
    service: Annotated[RatingService, Depends(ServiceFactory.rating_service_factory)],
    user_id: UserIDDep,
    rating_data: RatingAddRequestDTO,
):
    try:
        await service.rate(user_id=user_id, rating_data=rating_data)
    except ContentNotFoundException:
        raise ContentNotFoundHTTPException
    return {"status": "ok"}
