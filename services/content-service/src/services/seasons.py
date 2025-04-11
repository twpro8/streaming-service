from src.schemas.seasons import SeasonAddRequestDTO, SeasonPatchRequestDTO, SeasonAddDTO
from src.services.base import BaseService


class SeasonService(BaseService):
    async def get_seasons(self, series_id: int):
        seasons = await self.db.seasons.get_filtered(series_id=series_id)
        return seasons

    async def add_season(self, series_id: int, season_data: SeasonAddRequestDTO):
        new_data = SeasonAddDTO(
            series_id=series_id,
            **season_data.model_dump(),
        )
        season = await self.db.seasons.add(new_data)
        await self.db.commit()
        return season

    async def update_season(
        self, season_data: SeasonPatchRequestDTO, series_id: int, season_id: int
    ):
        await self.db.seasons.update(
            data=season_data,
            exclude_unset=True,
            id=season_id,
            series_id=series_id,
        )
        await self.db.commit()

    async def delete_season(self, series_id: int, season_id: int):
        await self.db.seasons.delete(id=season_id, series_id=series_id)
        await self.db.commit()
