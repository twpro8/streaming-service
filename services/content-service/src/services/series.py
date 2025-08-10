from datetime import date
from decimal import Decimal
from typing import List
from uuid import UUID

from src.enums import SortBy, SortOrder
from src.schemas.genres import SeriesGenreDTO
from src.schemas.series import (
    SeriesAddDTO,
    SeriesAddRequestDTO,
    SeriesPatchRequestDTO,
    SeriesPatchDTO,
)
from src.services.base import BaseService
from src.exceptions import (
    SeriesNotFoundException,
    UniqueCoverURLException,
    GenreNotFoundException,
)


class SeriesService(BaseService):
    async def get_series(
        self,
        page: int | None,
        per_page: int | None,
        title: str | None,
        description: str | None,
        director: str | None,
        release_year: date | None,
        release_year_ge: date | None,
        release_year_le: date | None,
        rating: Decimal | None,
        rating_ge: Decimal | None,
        rating_le: Decimal | None,
        genres: List[int] | None,
        sort_by: SortBy | None,
        sort_order: SortOrder | None,
    ):
        series = await self.db.series.get_filtered_series(
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
            genres=genres,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return series

    async def get_one_series(self, series_id: UUID):
        series = await self.db.series.get_one_or_none_with_rels(id=series_id)
        if series is None:
            raise SeriesNotFoundException
        return series

    async def add_series(self, series_data: SeriesAddRequestDTO):
        _series_data = SeriesAddDTO(**series_data.model_dump())
        try:
            series = await self.db.series.add_series(_series_data)
        except UniqueCoverURLException:
            raise

        if series_data.genres:
            _series_genres_data = [
                SeriesGenreDTO(series_id=series.id, genre_id=genre_id)
                for genre_id in series_data.genres
            ]
            try:
                await self.db.series_genres.add_series_genres(_series_genres_data)
            except GenreNotFoundException:
                raise

        await self.db.commit()
        return series

    async def update_series(self, series_id: UUID, series_data: SeriesPatchRequestDTO):
        if not await self.check_series_exists(id=series_id):
            raise SeriesNotFoundException

        _series_data = SeriesPatchDTO(**series_data.model_dump(exclude_unset=True))

        try:
            await self.db.series.update_series(
                id=series_id,
                data=_series_data,
                exclude_unset=True,
            )
        except UniqueCoverURLException:
            raise

        if series_data.genres_ids is not None:
            try:
                await self.db.series_genres.update_series_genres(
                    series_id=series_id,
                    genres_ids=series_data.genres_ids,
                )
            except GenreNotFoundException:
                raise

        await self.db.commit()

    async def delete_series(self, series_id: UUID):
        await self.db.series.delete(id=series_id)
        await self.db.commit()
