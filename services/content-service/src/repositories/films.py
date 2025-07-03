from datetime import date
from decimal import Decimal

from sqlalchemy import select, func

from src.models import FilmORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import FilmDataMapper
from src.schemas.films import FilmDTO


class FilmRepository(BaseRepository):
    model = FilmORM
    schema = FilmDTO
    mapper = FilmDataMapper

    async def get_filtered_films(
        self,
        page,
        per_page,
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
        query = select(self.model)
        if title is not None:
            query = query.filter(func.lower(self.model.title).contains(title.strip().lower()))
        if description is not None:
            query = query.filter(func.lower(self.model.description).contains(description.strip().lower()))
        if director is not None:
            query = query.filter(func.lower(self.model.director).contains(director.strip().lower()))
        if release_year is not None:
            query = query.filter(self.model.release_year == release_year)
        if release_year_ge is not None:
            query = query.filter(self.model.release_year >= release_year_ge)
        if release_year_le is not None:
            query = query.filter(self.model.release_year <= release_year_le)
        if rating is not None:
            query = query.filter(self.model.rating == rating)
        if rating_ge is not None:
            query = query.filter(self.model.rating >= rating_ge)
        if rating_le is not None:
            query = query.filter(self.model.rating <= rating_le)

        query = query.order_by(self.model.id).limit(per_page).offset((page - 1) * per_page)
        res = await self.session.execute(query)

        return [self.mapper.map_to_domain_entity(model) for model in res.scalars().all()]
