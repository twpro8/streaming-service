from datetime import datetime

from pydantic import BaseModel


class FriendshipDTO(BaseModel):
    id: int
    user_id: int
    friend_id: int
    created_at: datetime
