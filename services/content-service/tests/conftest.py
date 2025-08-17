from typing import Any, AsyncGenerator

import pytest

from httpx import AsyncClient, ASGITransport

from src.config import settings
from src.api.dependencies import get_db, get_admin, get_current_user_id
from src.db import null_pool_engine, null_pool_session_maker, DBManager
from src.models.base import Base
from src.models import *  # noqa
from src.main import app
from src.schemas.actors import ActorAddDTO, FilmActorDTO, SeriesActorDTO
from src.schemas.episodes import EpisodeDTO
from src.schemas.films import FilmDTO
from src.schemas.genres import GenreAddDTO, FilmGenreDTO, SeriesGenreDTO
from src.schemas.seasons import SeasonDTO
from src.schemas.series import SeriesDTO
from tests.utils import read_json


@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    assert settings.MODE == "TEST"


async def get_db_null_pool() -> AsyncGenerator[Any, Any]:
    async with DBManager(session_factory=null_pool_session_maker) as db:
        yield db


@pytest.fixture(scope="function")
async def db() -> AsyncGenerator[Any, Any]:
    async for db in get_db_null_pool():
        yield db


app.dependency_overrides[get_db] = get_db_null_pool  # noqa
app.dependency_overrides[get_admin] = lambda: None  # noqa
app.dependency_overrides[get_current_user_id] = lambda: 1  # The number is a user_id | # noqa


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    async with null_pool_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    films_data = [FilmDTO.model_validate(f) for f in read_json("films")]
    series_data = [SeriesDTO.model_validate(s) for s in read_json("series")]
    seasons_data = [SeasonDTO.model_validate(s) for s in read_json("seasons")]
    episodes_data = [EpisodeDTO.model_validate(e) for e in read_json("episodes")]
    genres_data = [GenreAddDTO.model_validate(g) for g in read_json("genres")]
    films_genres_data = [FilmGenreDTO.model_validate(fg) for fg in read_json("films_genres")]
    series_genres_data = [SeriesGenreDTO.model_validate(sg) for sg in read_json("series_genres")]
    actors_data = [ActorAddDTO.model_validate(ad) for ad in read_json("actors")]
    films_actors_data = [FilmActorDTO.model_validate(fa) for fa in read_json("films_actors")]
    series_actors_data = [SeriesActorDTO.model_validate(sa) for sa in read_json("series_actors")]

    async with DBManager(session_factory=null_pool_session_maker) as db_:
        await db_.films.add_bulk(films_data)
        await db_.series.add_bulk(series_data)
        await db_.seasons.add_bulk(seasons_data)
        await db_.episodes.add_bulk(episodes_data)
        await db_.genres.add_bulk(genres_data)
        await db_.films_genres.add_bulk(films_genres_data)
        await db_.series_genres.add_bulk(series_genres_data)
        await db_.actors.add_bulk(actors_data)
        await db_.films_actors.add_bulk(films_actors_data)
        await db_.series_actors.add_bulk(series_actors_data)
        await db_.commit()


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
async def get_series_ids():
    data = read_json("series")
    return [series_id["id"] for series_id in data]


@pytest.fixture
async def created_genres(ac):
    ids = []
    for name in ["TestGenre1", "TestGenre2", "TestGenre3"]:
        res = await ac.post("/genres", json={"name": name})
        assert res.status_code == 201
        ids.append(res.json()["data"]["id"])
    yield ids
    for genre_id in ids:
        await ac.delete(f"/genres/{genre_id}")


@pytest.fixture(scope="session")
async def max_pagination():
    return {"page": 1, "per_page": 30}


@pytest.fixture
async def get_all_films_with_rels(ac):
    films = []
    for film in read_json("films"):
        res = await ac.get(f"/films/{film['id']}")
        assert res.status_code == 200
        data = res.json()["data"]
        films.append(data)
    return films


@pytest.fixture
async def created_films(ac):
    films = []
    try:
        for i in range(700, 703):
            res = await ac.post(
                "/films",
                json={
                    "title": f"Python Movie{i}",
                    "description": f"Hola Amigo{i}",
                    "director": f"Mike Purple{i}",
                    "release_year": "1777-01-01",
                    "duration": 135,
                },
            )
            assert res.status_code == 201
            film = res.json()["data"]
            films.append(film)
        yield films
    finally:
        for film in films:
            await ac.delete(f"/films/{film['id']}")


@pytest.fixture
async def created_series(ac):
    series = []
    try:
        for i in range(704, 707):
            res = await ac.post(
                "/series",
                json={
                    "title": f"Python Movie{i}",
                    "description": f"Hola Amigo{i}",
                    "director": f"Mike Purple{i}",
                    "release_year": "1777-01-01",
                },
            )
            assert res.status_code == 201
            one_series = res.json()["data"]
            series.append(one_series)
        yield series
    finally:
        for s in series:
            await ac.delete(f"/series/{s['id']}")


@pytest.fixture(scope="session")
async def get_all_films():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        films = await db_.films.get_filtered()
        return [film.model_dump() for film in films]


@pytest.fixture(scope="session")
async def get_all_series():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        series = await db_.series.get_filtered()
        return [series.model_dump() for series in series]


@pytest.fixture(scope="session")
async def get_all_genres():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        genres = await db_.genres.get_filtered()
        return [genre.model_dump() for genre in genres]


@pytest.fixture(scope="session")
async def get_all_actors():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        actors = await db_.actors.get_filtered()
        return [actor.model_dump() for actor in actors]


@pytest.fixture(scope="session")
async def get_all_series_with_rels(ac):
    series = []
    for s in read_json("series"):
        res = await ac.get(f"/series/{s['id']}")
        assert res.status_code == 200
        data = res.json()["data"]
        series.append(data)
    return series


@pytest.fixture(scope="session")
async def get_all_seasons():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        seasons = await db_.seasons.get_filtered()
        return [season.model_dump() for season in seasons]


@pytest.fixture(scope="session")
async def get_all_episodes():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        episodes = await db_.episodes.get_filtered()
        return [episode.model_dump() for episode in episodes]
