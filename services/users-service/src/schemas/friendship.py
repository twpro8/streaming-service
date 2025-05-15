from datetime import datetime

from pydantic import BaseModel

from src.schemas.pydatic_types import IDInt


class FriendshipDTO(BaseModel):
    id: IDInt
    user_id: IDInt
    friend_id: IDInt
    created_at: datetime
