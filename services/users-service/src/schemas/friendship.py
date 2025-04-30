from datetime import datetime

from pydantic import BaseModel

from src.schemas.pydatic_types import TypeID


class FriendshipDTO(BaseModel):
    id: TypeID
    user_id: TypeID
    friend_id: TypeID
    created_at: datetime
