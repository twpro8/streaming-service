from fastapi import APIRouter

from src.schemas.rating import RatingAddRequestDTO
from src.services.rating import RatingService
from src.views.dependencies import DBDep, UserDep


router = APIRouter(prefix="/ratings", tags=["Ratings"])


@router.post("")
async def rate_content(db: DBDep, user_id: UserDep, rating_data: RatingAddRequestDTO):
    await RatingService(db).rate(user_id=user_id, data=rating_data)
    return {"status": "ok"}
