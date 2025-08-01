from uuid import UUID

from src.exceptions import (
    SeasonNotFoundException,
    ObjectAlreadyExistsException,
    SeriesNotFoundException,
    UniqueSeasonNumberException,
    UniqueSeasonPerSeriesException,
)
from src.schemas.seasons import SeasonPatchRequestDTO, SeasonAddDTO
from src.services.base import BaseService


class SeasonService(BaseService):
    async def get_seasons(self, series_id: UUID, page: int, per_page: int):
        seasons = await self.db.seasons.get_filtered(
            series_id=series_id,
            page=page,
            per_page=per_page,
        )
        return seasons

    async def get_season(self, season_id: UUID):
        season = await self.db.seasons.get_one_or_none(id=season_id)
        if not season:
            raise SeasonNotFoundException
        return season

    async def add_season(self, season_data: SeasonAddDTO):
        if not await self.check_series_exists(id=season_data.series_id):
            raise SeriesNotFoundException
        try:
            season = await self.db.seasons.add_season(season_data)
        except UniqueSeasonPerSeriesException:
            raise
        await self.db.commit()
        return season

    async def update_season(self, season_data: SeasonPatchRequestDTO, season_id: UUID):
        if not await self.check_season_exists(id=season_id):
            raise SeasonNotFoundException

        try:
            await self.db.seasons.update(
                id=season_id,
                data=season_data,
                exclude_unset=True,
            )
        except ObjectAlreadyExistsException:
            raise UniqueSeasonNumberException
        await self.db.commit()

    async def delete_season(self, season_id: UUID):
        await self.db.seasons.delete(id=season_id)
        await self.db.commit()
