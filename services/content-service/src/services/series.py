from uuid import UUID

from pydantic import BaseModel

from src.services.base import BaseService
from src.exceptions import ObjectNotFoundException, SeriesNotFoundException


class SeriesService(BaseService):
    async def add_series(self, data: BaseModel):
        series = await self.db.series.add(data)
        await self.db.commit()
        return series

    async def get_series(self, page: int, per_page: int):
        series = await self.db.series.get_filtered(page=page, per_page=per_page)
        return series

    async def get_one_series(self, series_id: UUID):
        try:
            series = await self.db.series.get_one(id=series_id)
        except ObjectNotFoundException:
            raise SeriesNotFoundException
        return series

    async def replace_series(self, series_id: UUID, series_data: BaseModel):
        if not await self.check_series_exists(id=series_id):
            raise SeriesNotFoundException

        await self.db.series.update(id=series_id, data=series_data)
        await self.db.commit()

    async def update_series(self, series_id: UUID, series_data: BaseModel):
        if not await self.check_series_exists(id=series_id):
            raise SeriesNotFoundException

        await self.db.series.update(id=series_id, data=series_data, exclude_unset=True)
        await self.db.commit()

    async def delete_series(self, series_id: UUID):
        await self.db.series.delete(id=series_id)
        await self.db.commit()
