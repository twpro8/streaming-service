from pydantic import BaseModel

from src.services.base import BaseService


class SeriesService(BaseService):
    async def add_series(self, data: BaseModel):
        series = await self.db.series.add_one(data)
        await self.db.commit()
        return series
