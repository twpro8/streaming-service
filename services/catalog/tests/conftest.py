from typing import Any, AsyncGenerator

import pytest
from alembic import command
from alembic.config import Config

from httpx import AsyncClient, ASGITransport
from sqlalchemy.util import greenlet_spawn
from uuid_extensions import uuid7str

from src.config import settings
from src.api.dependencies import get_admin, get_current_user_id
from src.db import null_pool_engine, null_pool_session_maker
from src.factories.db_manager import DBManagerFactory
from src.managers.db import DBManager
from src.models import *  # noqa
from src.main import app
from src.schemas.actors import ActorAddDTO, MovieActorDTO, ShowActorDTO
from src.schemas.comments import CommentAddDTO
from src.schemas.countries import CountryAddDTO, MovieCountryDTO, ShowCountryDTO
from src.schemas.directors import DirectorAddDTO, MovieDirectorDTO, ShowDirectorDTO
from src.schemas.episodes import EpisodeAddDTO
from src.schemas.languages import LanguageAddDTO
from src.schemas.movies import MovieDTO
from src.schemas.genres import GenreAddDTO, MovieGenreDTO, ShowGenreDTO
from src.schemas.seasons import SeasonAddDTO
from src.schemas.shows import ShowDTO
from tests.utils import read_json


user_id = uuid7str()


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


app.dependency_overrides[DBManagerFactory.get_db] = get_db_null_pool
app.dependency_overrides[get_admin] = lambda: None
app.dependency_overrides[get_current_user_id] = lambda: user_id


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    async with null_pool_engine.begin() as conn:
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.attributes["connection"] = conn
        await greenlet_spawn(lambda: command.downgrade(alembic_cfg, "base"))
        await greenlet_spawn(lambda: command.upgrade(alembic_cfg, "head"))

    movies_data = [MovieDTO.model_validate(obj) for obj in read_json("movies")]
    shows_data = [ShowDTO.model_validate(obj) for obj in read_json("shows")]
    seasons_data = [SeasonAddDTO.model_validate(obj) for obj in read_json("seasons")]
    episodes_data = [EpisodeAddDTO.model_validate(obj) for obj in read_json("episodes")]
    directors_data = [DirectorAddDTO.model_validate(obj) for obj in read_json("actors")]
    actors_data = [ActorAddDTO.model_validate(obj) for obj in read_json("actors")]
    genres_data = [GenreAddDTO.model_validate(obj) for obj in read_json("genres")]
    movies_genres_data = [MovieGenreDTO.model_validate(obj) for obj in read_json("movies_genres")]
    shows_genres_data = [ShowGenreDTO.model_validate(obj) for obj in read_json("shows_genres")]
    movies_actors_data = [MovieActorDTO.model_validate(obj) for obj in read_json("movies_actors")]
    movies_directors_data = [
        MovieDirectorDTO.model_validate(obj) for obj in read_json("movies_directors")
    ]
    shows_actors_data = [ShowActorDTO.model_validate(obj) for obj in read_json("shows_actors")]
    shows_directors_data = [
        ShowDirectorDTO.model_validate(obj) for obj in read_json("shows_directors")
    ]
    comments_data = [
        CommentAddDTO.model_validate({**obj, "user_id": user_id}) for obj in read_json("comments")
    ]
    languages = [LanguageAddDTO.model_validate(obj) for obj in read_json("languages")]
    countries = [CountryAddDTO.model_validate(obj) for obj in read_json("countries")]
    movies_countries_data = [
        MovieCountryDTO.model_validate(obj) for obj in read_json("movies_countries")
    ]
    shows_countries_data = [
        ShowCountryDTO.model_validate(obj) for obj in read_json("shows_countries")
    ]

    async with DBManager(session_factory=null_pool_session_maker) as db_:
        await db_.movies.add_bulk(movies_data)
        await db_.shows.add_bulk(shows_data)
        await db_.seasons.add_bulk(seasons_data)
        await db_.episodes.add_bulk(episodes_data)
        await db_.genres.add_bulk(genres_data)
        await db_.movies_genres.add_bulk(movies_genres_data)
        await db_.shows_genres.add_bulk(shows_genres_data)
        await db_.directors.add_bulk(directors_data)
        await db_.actors.add_bulk(actors_data)
        await db_.movies_actors.add_bulk(movies_actors_data)
        await db_.shows_actors.add_bulk(shows_actors_data)
        await db_.comments.add_bulk(comments_data)
        await db_.languages.add_bulk(languages)
        await db_.countries.add_bulk(countries)
        await db_.movies_directors.add_bulk(movies_directors_data)
        await db_.shows_directors.add_bulk(shows_directors_data)
        await db_.movies_countries.add_bulk(movies_countries_data)
        await db_.shows_countries.add_bulk(shows_countries_data)
        await db_.commit()


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def created_genres(ac):
    ids = []
    for name in ["TestGenre1", "TestGenre2", "TestGenre3"]:
        res = await ac.post("/v1/genres", json={"name": name})
        assert res.status_code == 201
        ids.append(res.json()["data"]["id"])
    yield ids
    for genre_id in ids:
        await ac.delete(f"/v1/genres/{genre_id}")


@pytest.fixture(scope="session")
async def max_pagination():
    return {"page": 1, "per_page": 100}


@pytest.fixture
async def get_all_movies_with_rels(ac):
    movies = []
    for movie in read_json("movies"):
        res = await ac.get(f"/v1/movies/{movie['id']}")
        assert res.status_code == 200
        data = res.json()["data"]
        movies.append(data)
    return movies


@pytest.fixture
async def created_movies(ac):
    movies = []
    try:
        for i in range(700, 703):
            res = await ac.post(
                "/v1/movies",
                json={
                    "title": f"Python Movie{i}",
                    "description": f"Hola Amigo{i}",
                    "release_date": "1777-01-01",
                    "duration": 135,
                },
            )
            assert res.status_code == 201
            movie = res.json()["data"]
            movies.append(movie)
        yield movies
    finally:
        for movie in movies:
            await ac.delete(f"/v1/movies/{movie['id']}")


@pytest.fixture
async def created_shows(ac):
    shows = []
    try:
        for i in range(704, 707):
            res = await ac.post(
                "/v1/shows",
                json={
                    "title": f"Python Movie{i}",
                    "description": f"Hola Amigo{i}",
                    "release_date": "1777-01-01",
                },
            )
            assert res.status_code == 201
            show = res.json()["data"]
            shows.append(show)
        yield shows
    finally:
        for s in shows:
            await ac.delete(f"/v1/shows/{s['id']}")


@pytest.fixture
async def created_languages(ac):
    langs = []
    mock_data = ["he", "vi", "th", "id", "no"]
    try:
        for code in mock_data:
            res = await ac.post("/v1/languages", json={"code": code})
            assert res.status_code == 201
            lang = res.json()["data"]
            langs.append(lang)
        yield langs
    finally:
        for s in langs:
            await ac.delete(f"/v1/shows/{s['id']}")


@pytest.fixture(scope="function")
async def get_all_comments():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        comments = await db_.comments.get_filtered()
        return [comment.model_dump(mode="json") for comment in comments]


@pytest.fixture(scope="function")
async def get_all_movies():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        movies = await db_.movies.get_filtered_movies(sort_by="id", sort_order="desc")
        return [movie.model_dump(mode="json") for movie in movies]


@pytest.fixture(scope="function")
async def get_all_shows():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        shows = await db_.shows.get_filtered_shows(sort_by="id", sort_order="desc")
        return [show.model_dump(mode="json") for show in shows]


@pytest.fixture(scope="session")
async def get_all_genres():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        genres = await db_.genres.get_filtered()
        return [genre.model_dump(mode="json") for genre in genres]


@pytest.fixture(scope="function")
async def get_all_actors():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        actors = await db_.actors.get_filtered()
        return [actor.model_dump(mode="json") for actor in actors]


@pytest.fixture(scope="function")
async def get_all_directors():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        directors = await db_.directors.get_filtered()
        return [director.model_dump(mode="json") for director in directors]


@pytest.fixture(scope="session")
async def get_all_shows_with_rels(ac):
    shows = []
    for s in read_json("shows"):
        res = await ac.get(f"/v1/shows/{s['id']}")
        assert res.status_code == 200
        data = res.json()["data"]
        shows.append(data)
    return shows


@pytest.fixture(scope="function")
async def get_all_seasons():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        seasons = await db_.seasons.get_filtered()
        return [season.model_dump(mode="json") for season in seasons]


@pytest.fixture(scope="function")
async def get_all_episodes():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        episodes = await db_.episodes.get_filtered()
        return [episode.model_dump(mode="json") for episode in episodes]


@pytest.fixture(scope="session")
async def get_all_languages():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        languages = await db_.languages.get_filtered()
        return [lang.model_dump(mode="json") for lang in languages]


@pytest.fixture(scope="session")
async def get_all_countries():
    async with DBManager(session_factory=null_pool_session_maker) as db_:
        countries = await db_.countries.get_filtered()
        return [country.model_dump(mode="json") for country in countries]


@pytest.fixture(scope="session")
async def current_user_id() -> str:
    return user_id
