from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from src.services.base import BaseService
from src.exceptions import ObjectNotFoundException, SeriesNotFoundException, UniqueCoverURLException


class SeriesService(BaseService):
    async def get_series(
        self,
        page: int,
        per_page: int,
        title: str | None,
        description: str | None,
        director: str | None,
        release_year: date | None,
        release_year_ge: date | None,
        release_year_le: date | None,
        rating: Decimal | None,
        rating_ge: Decimal | None,
        rating_le: Decimal | None,
    ):
        series = await self.db.series.get_filtered_films_or_series(
            page=page,
            per_page=per_page,
            title=title,
            description=description,
            director=director,
            release_year=release_year,
            release_year_ge=release_year_ge,
            release_year_le=release_year_le,
            rating=rating,
            rating_ge=rating_ge,
            rating_le=rating_le,
        )
        return series

    async def get_one_series(self, series_id: UUID):
        try:
            series = await self.db.series.get_one(id=series_id)
        except ObjectNotFoundException:
            raise SeriesNotFoundException
        return series

    async def add_series(self, data: BaseModel):
        try:
            series = await self.db.series.add_series(data)
        except UniqueCoverURLException:
            raise
        await self.db.commit()
        return series

    async def update_series(self, series_id: UUID, series_data: BaseModel):
        if not await self.check_series_exists(id=series_id):
            raise SeriesNotFoundException
        try:
            await self.db.series.update_series(
                id=series_id,
                data=series_data,
                exclude_unset=True,
            )
        except UniqueCoverURLException:
            raise
        await self.db.commit()

    async def delete_series(self, series_id: UUID):
        await self.db.series.delete(id=series_id)
        await self.db.commit()
