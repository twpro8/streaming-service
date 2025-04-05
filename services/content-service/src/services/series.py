from typing import List

from pydantic import BaseModel

from src.services.base import BaseService


class SeriesService(BaseService):
    async def add_series(self, data: BaseModel):
        series = await self.db.series.add_one(data)
        await self.db.commit()
        return series

    async def get_series(self, ids: List[int | None]):
        series = await self.db.series.get_objects_by_ids(ids)
        return series
