from fastapi import APIRouter

from src.exceptions import ContentNotFoundException, ContentNotFoundHTTPException
from src.schemas.rating import RatingAddRequestDTO
from src.services.rating import RatingService
from src.api.dependencies import DBDep, UserDep


v1_router = APIRouter(prefix="/v1/ratings", tags=["ratings"])


@v1_router.post("")
async def rate_content(db: DBDep, user_id: UserDep, rating_data: RatingAddRequestDTO):
    try:
        await RatingService(db).rate(user_id=user_id, data=rating_data)
    except ContentNotFoundException:
        raise ContentNotFoundHTTPException
    return {"status": "ok"}
