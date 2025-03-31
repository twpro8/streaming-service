from pydantic import BaseModel


class FavoriteDTO(BaseModel):
    id: int
    user_id: int
    film_id: int


class FavoriteAddDTO(BaseModel):
    user_id: int
    film_id: int
