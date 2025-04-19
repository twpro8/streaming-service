from typing import List

from pydantic import BaseModel

from src.services.base import BaseService


class SeriesService(BaseService):
    async def add_series(self, data: BaseModel):
        series = await self.db.series.add(data)
        await self.db.commit()
        return series

    async def get_series(self, series_ids: List[int | None] = None):
        if series_ids is not None:
            series = await self.db.series.get_objects_by_ids(series_ids)
            return series
        series = await self.db.series.get_filtered()
        return series

    async def update_entire_series(self, series_id: int, series_data: BaseModel):
        await self.db.series.update(id=series_id, data=series_data)
        await self.db.commit()

    async def partly_update_series(self, series_id: int, series_data: BaseModel):
        await self.db.series.update(id=series_id, data=series_data, exclude_unset=True)
        await self.db.commit()

    async def delete_series(self, series_id: int):
        await self.db.series.delete(id=series_id)
        await self.db.commit()
