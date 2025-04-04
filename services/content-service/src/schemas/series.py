from datetime import date

from pydantic import BaseModel


class SeriesDTO(BaseModel):
    id: int
    title: str
    description: str
    director: str
    release_year: date
    rating: float
    cover_id: int
