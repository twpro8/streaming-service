from itertools import islice

import pytest
from uuid_extensions import uuid7str

from tests.utils import get_and_validate, count_content, calculate_expected_length


@pytest.mark.order(1)
async def test_movies_pagination(ac, get_all_movies):
    per_page = 2
    for page in range(1, 10):
        data = await get_and_validate(
            ac=ac,
            url="/v1/movies",
            params={
                "page": page,
                "per_page": per_page,
            },
        )
        expected_length = calculate_expected_length(page, per_page, len(get_all_movies))
        assert len(data) == expected_length


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "field, order",
    [
        ("id", "asc"),
        ("id", "desc"),
        ("title", "asc"),
        ("title", "desc"),
        ("year", "asc"),
        ("year", "desc"),
        ("rating", "asc"),
        ("rating", "desc"),
        ("created_at", "asc"),
        ("created_at", "desc"),
        ("updated_at", "asc"),
        ("updated_at", "desc"),
    ],
)
async def test_movies_sorting(ac, field, order, max_pagination):
    data = await get_and_validate(
        ac=ac,
        url="/v1/movies",
        params={
            "sort": f"{field}:{order}",
            **max_pagination,
        },
    )
    # Extract field values for sorting
    if field == "year":
        values = [int(movie["release_date"][:4]) for movie in data]
    elif field == "id":
        values = [movie["id"] for movie in data]
    elif field == "rating":
        values = [float(movie["rating"]) for movie in data]
    elif field == "title":
        values = [movie["title"] for movie in data]
    elif field == "created_at":
        values = [movie["created_at"] for movie in data]
    elif field == "updated_at":
        values = [movie["updated_at"] for movie in data]
    else:
        raise AssertionError(f"Unknown field: {field}")
    sorted_values = sorted(values, reverse=(order == "desc"))
    assert values == sorted_values


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "title",
    [
        " hidden",
        "chamber ",
        " THE ",
        "no match",
        "meet dave",
    ],
)
async def test_filter_by_title(ac, title, get_all_movies, max_pagination):
    data = await get_and_validate(
        ac=ac,
        url="/v1/movies",
        params={
            "title": title,
            **max_pagination,
        },
    )
    expected_count = count_content(items=get_all_movies, field="title", value=title)
    assert len(data) == expected_count


@pytest.mark.order(1)
@pytest.mark.parametrize("year", [2000, 2003, 2004, 1999])
async def test_filter_by_exact_release_year(ac, year, get_all_movies, max_pagination):
    expected_count = sum(1 for movie in get_all_movies if year == int(movie["release_date"][:4]))
    data = await get_and_validate(
        ac=ac,
        url="/v1/movies",
        params={
            "year": year,
            **max_pagination,
        },
    )
    assert len(data) == expected_count


@pytest.mark.order(1)
@pytest.mark.parametrize("year_gt", [1899, 2003, 2010, 2100])
async def test_filter_by_release_year_gt(ac, year_gt, get_all_movies, max_pagination):
    expected_count = sum(1 for movie in get_all_movies if int(movie["release_date"][:4]) > year_gt)

    data = await get_and_validate(
        ac=ac,
        url="/v1/movies",
        params={
            "year_gt": year_gt,
            **max_pagination,
        },
    )
    assert len(data) == expected_count


@pytest.mark.order(1)
@pytest.mark.parametrize("year_lt", [1999, 2003, 2005, 2010])
async def test_filter_by_release_year_lt(ac, year_lt, get_all_movies, max_pagination):
    expected_count = sum(1 for movie in get_all_movies if int(movie["release_date"][:4]) < year_lt)

    data = await get_and_validate(
        ac=ac,
        url="/v1/movies",
        params={
            "year_lt": year_lt,
            **max_pagination,
        },
    )
    assert len(data) == expected_count


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "year_gt, year_lt",
    [
        (2002, 2004),
        (1956, 2025),
        (1899, 1952),
    ],
)
async def test_filter_by_release_year_range(
    ac,
    year_gt,
    year_lt,
    get_all_movies,
    max_pagination,
):
    expected_count = sum(
        1 for movie in get_all_movies if year_gt < int(movie["release_date"][:4]) < year_lt
    )
    data = await get_and_validate(
        ac=ac,
        url="/v1/movies",
        params={
            "year_gt": year_gt,
            "year_lt": year_lt,
            **max_pagination,
        },
    )
    assert len(data) == expected_count


@pytest.mark.order(1)
@pytest.mark.parametrize("rating", (0.0, 1.0, 5.0, 7.0, 8.0))
async def test_filter_by_exact_rating(ac, rating, get_all_movies, max_pagination):
    expected_count = sum(1 for movie in get_all_movies if rating == float(movie["rating"]))
    data = await get_and_validate(
        ac=ac,
        url="/v1/movies",
        params={
            "rating": rating,
            **max_pagination,
        },
    )
    assert len(data) == expected_count


@pytest.mark.order(1)
@pytest.mark.parametrize("rating_gt", [0.0, 2.0, 5.0, 9.0])
async def test_filter_by_rating_gt(ac, rating_gt, get_all_movies, max_pagination):
    expected_count = sum(1 for movie in get_all_movies if rating_gt < float(movie["rating"]))
    data = await get_and_validate(
        ac=ac,
        url="/v1/movies",
        params={
            "rating_gt": rating_gt,
            **max_pagination,
        },
    )
    assert len(data) == expected_count


@pytest.mark.order(1)
@pytest.mark.parametrize("rating_lt", [4.0, 5.0, 9.0])
async def test_filter_by_rating_lt(ac, rating_lt, get_all_movies, max_pagination):
    expected_count = sum(1 for movie in get_all_movies if rating_lt > float(movie["rating"]))
    data = await get_and_validate(
        ac=ac,
        url="/v1/movies",
        params={
            "rating_lt": rating_lt,
            **max_pagination,
        },
    )
    assert len(data) == expected_count


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "rating_gt, rating_lt",
    (
        (0.0, 0.3),
        (5.0, 7.6),
        (1.0, 4.5),
        (5.0, 6.0),
        (7.5, 9.0),
    ),
)
async def test_filter_by_rating_range(ac, rating_gt, rating_lt, get_all_movies, max_pagination):
    expected_count = sum(
        1 for movie in get_all_movies if rating_gt < float(movie["rating"]) < rating_lt
    )
    data = await get_and_validate(
        ac=ac,
        url="/v1/movies",
        params={
            "rating_gt": rating_gt,
            "rating_lt": rating_lt,
            **max_pagination,
        },
    )
    assert len(data) == expected_count


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "set_indexes",
    [
        [1, 4],
        [1, 3, 4],
        [1],
        [2],
        [0, 1, 2, 3, 4],
        [4],
    ],
)
async def test_filter_by_directors(
    ac,
    set_indexes,
    get_all_directors,
    get_all_movies_with_rels,
    max_pagination,
):
    directors_ids = [get_all_directors[i]["id"] for i in set_indexes]
    expected_count = sum(
        1
        for movie in get_all_movies_with_rels
        if any(director["id"] in directors_ids for director in movie["directors"])
    )
    data = await get_and_validate(
        ac=ac,
        url="/v1/movies",
        params={
            "directors_ids": directors_ids,
            **max_pagination,
        },
    )
    assert len(data) == expected_count


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "set_indexes",
    [
        [0, 1, 2, 3, 4],
        [1, 4],
        [1, 3, 4],
        [1],
        [2],
        [4],
    ],
)
async def test_get_filter_by_actors(
    ac,
    set_indexes,
    get_all_actors,
    get_all_movies_with_rels,
    max_pagination,
):
    actors_ids = [get_all_actors[i]["id"] for i in set_indexes]
    expected_count = sum(
        1
        for movie in get_all_movies_with_rels
        if any(actor["id"] in actors_ids for actor in movie["actors"])
    )
    data = await get_and_validate(
        ac, "/v1/movies", params={"actors_ids": actors_ids, **max_pagination}
    )
    assert len(data) == expected_count


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "genres_ids",
    [
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        [2, 4, 6, 8, 10],
        [1, 3, 5, 7, 9],
        [2, 4, 6, 8],
        [1],
        [2],
        [3],
        [4],
        [5],
        [6],
        [7],
        [8],
        [9],
        [10],
        [1, 2, 3],
    ],
)
async def test_get_filter_by_genres(ac, genres_ids, get_all_movies_with_rels, max_pagination):
    expected_count = sum(
        1
        for movie in get_all_movies_with_rels
        if any(genre["id"] in genres_ids for genre in movie["genres"])
    )
    data = await get_and_validate(
        ac=ac,
        url="/v1/movies",
        params={
            "genres_ids": genres_ids,
            **max_pagination,
        },
    )
    assert len(data) == expected_count


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "countries_ids",
    [
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        [2, 4, 6, 8, 10],
        [1, 3, 5, 7, 9],
        [2, 4, 6, 8],
        [1],
        [2],
        [3],
        [4],
        [5],
        [6],
        [7],
        [8],
        [9],
        [10],
        [1, 2, 3],
    ],
)
async def test_get_filter_by_countries(ac, countries_ids, get_all_movies_with_rels, max_pagination):
    expected_count = sum(
        1
        for movie in get_all_movies_with_rels
        if any(country["id"] in countries_ids for country in movie["countries"])
    )
    data = await get_and_validate(
        ac=ac,
        url="/v1/movies",
        params={
            "countries_ids": countries_ids,
            **max_pagination,
        },
    )
    assert len(data) == expected_count


@pytest.mark.parametrize(
    "field",
    (
        "year",
        "year_gt",
        "year_lt",
        "rating",
        "rating_gt",
        "rating_lt",
        "sort",
        "directors_ids",
        "actors_ids",
        "genres_ids",
        "countries_ids",
        "title",
    ),
)
async def test_invalid_query_params(ac, field):
    value = "invalid" if field != "title" else 11
    res = await ac.get("/v1/movies", params={field: value})
    assert res.status_code == 422
    assert "detail" in res.json()


@pytest.mark.order(1)
async def test_get_movie(ac, get_all_movies):
    for movie in islice(get_all_movies, 2):
        data = await get_and_validate(
            ac=ac,
            url=f"/v1/movies/{movie['id']}",
            expect_list=False,
        )
        assert isinstance(data, dict)
        assert data["id"] == movie["id"]
        assert data["title"] == movie["title"]
        assert data["description"] == movie["description"]
        assert data["release_date"] == movie["release_date"]
        assert data["duration"] == movie["duration"]
        assert data["rating"] == movie["rating"]
        assert data["cover_url"] == movie["cover_url"]
        assert data["video_url"] == movie["video_url"]
        assert data["created_at"] == movie["created_at"]
        assert data["updated_at"] == movie["updated_at"]


async def test_get_movie_not_found(ac):
    res = await ac.get(f"/v1/movies/{uuid7str()}")
    assert res.status_code == 404
    assert "detail" in res.json()


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "title, description, release_date, duration",
    [
        (
            "Valid Title",
            "Valid Description",
            "2005-01-01",
            140,
        ),
        (
            "Valid Title2",
            "Valid Description2",
            "2006-01-01",
            135,
        ),
    ],
)
async def test_add_valid_data_without_optional(ac, title, description, release_date, duration):
    res = await ac.post(
        "/v1/movies",
        json={
            "title": title,
            "description": description,
            "release_date": release_date,
            "duration": duration,
        },
    )
    assert res.status_code == 201

    movie_id = res.json()["data"]["id"]
    added_movie = await get_and_validate(
        ac=ac,
        url=f"/v1/movies/{movie_id}",
        expect_list=False,
    )

    assert added_movie["title"] == title
    assert added_movie["description"] == description
    assert added_movie["release_date"] == release_date
    assert added_movie["duration"] == duration


@pytest.mark.order(1)
@pytest.mark.parametrize(
    """
    title,
    description,
    release_date,
    duration,
    cover_url,
    directors_indexes,
    actors_indexes,
    genres_ids,
    countries_ids
    """,
    [
        (
            "Valid Title",
            "Valid Description",
            "2007-01-01",
            135,
            f"https://{uuid7str()}/pic.jpg",
            [0, 1, 2],
            [0, 1, 2],
            [1, 2, 3],
            [1, 2, 3],
        ),
        (
            "Valid Title4",
            "Valid Description4",
            "2008-01-01",
            135,
            f"https://{uuid7str()}/pic.jpg",
            [0, 1, 2],
            [0, 1, 2],
            [1, 2, 3],
            [1, 2, 3],
        ),
    ],
)
async def test_add_valid_data_with_optional(
    ac,
    get_all_actors,
    get_all_directors,
    title,
    description,
    release_date,
    duration,
    cover_url,
    directors_indexes,
    actors_indexes,
    genres_ids,
    countries_ids,
):
    directors_ids = [get_all_directors[i]["id"] for i in directors_indexes]
    actors_ids = [get_all_actors[i]["id"] for i in actors_indexes]
    res = await ac.post(
        "/v1/movies",
        json={
            "title": title,
            "description": description,
            "release_date": release_date,
            "duration": duration,
            "cover_url": cover_url,
            "directors_ids": directors_ids,
            "actors_ids": actors_ids,
            "genres_ids": genres_ids,
            "countries_ids": countries_ids,
        },
    )
    assert res.status_code == 201

    movie_id = res.json()["data"]["id"]
    added_movie = await get_and_validate(
        ac=ac,
        url=f"/v1/movies/{movie_id}",
        expect_list=False,
    )

    assert added_movie["title"] == title
    assert added_movie["description"] == description
    assert added_movie["release_date"] == release_date
    assert added_movie["duration"] == duration
    assert added_movie["cover_url"] == cover_url

    assert len(added_movie["directors"]) == len(directors_ids)
    assert len(added_movie["actors"]) == len(actors_ids)
    assert len(added_movie["genres"]) == len(genres_ids)
    assert len(added_movie["countries"]) == len(countries_ids)

    assert all(director["id"] in directors_ids for director in added_movie["directors"])
    assert all(actor["id"] in actors_ids for actor in added_movie["actors"])
    assert all(genre["id"] in genres_ids for genre in added_movie["genres"])
    assert all(country["id"] in countries_ids for country in added_movie["countries"])

    assert "rating" in added_movie
    assert added_movie["created_at"]
    assert added_movie["updated_at"]


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "field, value",
    (
        ("title", "t"),
        ("title", "t" * 257),
        ("description", "d"),
        ("description", "d" * 1025),
        ("release_date", "999-01-01"),
        ("release_date", "2100-01-01"),
        ("duration", 0),
        ("cover_url", "invalid-url"),
        ("directors_ids", ["invalid-uuid"]),
        ("actors_ids", ["invalid-uuid"]),
        ("genres_ids", [0, 0]),
        ("countries_ids", [0, 0]),
        ("extra", "unknown"),
    ),
)
async def test_add_movie_invalid(ac, field, value):
    req_body = {
        "title": "Valid Title 5",
        "description": "Valid Description 5",
        "release_date": "2020-01-01",
        "duration": 135,
        "cover_url": f"https://{uuid7str()}/pic.jpg",
        field: value,
    }
    res = await ac.post("/v1/movies", json=req_body)
    assert res.status_code == 422
    assert "detail" in res.json()


@pytest.mark.order(1)
async def test_add_movie_on_conflict(ac, get_all_movies):
    for movie in islice(get_all_movies, 2):
        res = await ac.post(
            url="/v1/movies",
            json={
                "title": movie["title"],
                "description": "Some description",
                "release_date": movie["release_date"],
                "duration": 135,
            },
        )
        assert res.status_code == 409


@pytest.mark.order(1)
async def test_add_movie_on_conflict_cover_url(ac, get_all_movies):
    cover_url = next((m["cover_url"] for m in get_all_movies if m["cover_url"]), None)
    assert cover_url is not None, "at least one movie with cover url is required"

    res = await ac.post(
        url="/v1/movies",
        json={
            "title": "valid title for conflict test",
            "description": "valid description for conflict test",
            "release_date": "1988-01-01",
            "duration": 135,
            "cover_url": cover_url,
        },
    )
    assert res.status_code == 409
    assert "detail" in res.json()


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "field, value",
    [
        ("directors_ids", [uuid7str()]),
        ("actors_ids", [uuid7str()]),
        ("genres_ids", [999]),
        ("countries_ids", [999]),
    ],
)
async def test_add_movie_not_found(ac, field, value):
    req_body = {
        "title": "NotFoundTitle",
        "description": "NotFoundDescription",
        "release_date": "2020-01-01",
        "duration": 135,
        "cover_url": f"https://{uuid7str()}/pic.jpg",
        field: value,
    }
    res = await ac.post("/v1/movies", json=req_body)
    assert res.status_code == 404
    assert "detail" in res.json()


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "field,value",
    [
        ("title", "Title Updated 1"),
        ("title", "Title Updated 2"),
        ("description", "Description Updated 1"),
        ("description", "Description Updated 2"),
        ("release_date", "1888-01-01"),
        ("release_date", "1999-07-07"),
        ("duration", 111),
        ("duration", 222),
        ("duration", 333),
        ("cover_url", f"https://{uuid7str()}/pic.jpg"),
        ("cover_url", None),
        ("video_url", f"https://{uuid7str()}/video.mp4"),
        ("video_url", None),
    ],
)
async def test_update_field_valid(ac, get_all_movies, field, value):
    movie = get_all_movies[0]

    res = await ac.patch(f"/v1/movies/{movie['id']}", json={field: value})
    assert res.status_code == 200

    updated_movie = await get_and_validate(
        ac=ac,
        url=f"/v1/movies/{movie['id']}",
        expect_list=False,
    )

    assert isinstance(updated_movie, dict)
    assert updated_movie["id"] == movie["id"]
    assert updated_movie[field] == value

    unchanged_fields = (
        "title",
        "description",
        "release_date",
        "duration",
        "cover_url",
        "video_url",
    )
    for f in unchanged_fields:
        if f != field:
            assert updated_movie[f] == movie[f]

    assert updated_movie["rating"] == movie["rating"]
    assert updated_movie["created_at"] == movie["created_at"]
    assert updated_movie["updated_at"] != movie["updated_at"]


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "directors_indexes", [[0, 1, 2], [2, 3], [5, 7, 9], [0, 4, 2], [], [7, 8, 1]]
)
async def test_update_movies_directors(ac, get_all_directors, get_all_movies, directors_indexes):
    movie_id = get_all_movies[0]["id"]
    directors_ids = [get_all_directors[i]["id"] for i in directors_indexes]

    res = await ac.patch(f"/v1/movies/{movie_id}", json={"directors_ids": directors_ids})
    assert res.status_code == 200

    updated_movie = await get_and_validate(
        ac=ac,
        url=f"/v1/movies/{movie_id}",
        expect_list=False,
    )

    assert len(updated_movie["directors"]) == len(directors_indexes)
    assert all(director["id"] in directors_ids for director in updated_movie["directors"])


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "actors_indexes", [[0, 1, 2], [2, 3], [], [5, 7, 9], [0, 4, 2], [], [7, 8, 1]]
)
async def test_update_movies_actors(ac, get_all_actors, get_all_movies, actors_indexes):
    movie_id = get_all_movies[0]["id"]
    actors_ids = [get_all_actors[i]["id"] for i in actors_indexes]

    res = await ac.patch(f"/v1/movies/{movie_id}", json={"actors_ids": actors_ids})
    assert res.status_code == 200

    updated_movie = await get_and_validate(
        ac=ac,
        url=f"/v1/movies/{movie_id}",
        expect_list=False,
    )

    assert len(updated_movie["actors"]) == len(actors_indexes)
    assert all(actor["id"] in actors_ids for actor in updated_movie["actors"])


@pytest.mark.order(1)
@pytest.mark.parametrize("genres_ids", [[7, 8, 9], [2, 3, 7], [], [1, 2, 3]])
async def test_update_movies_genres(ac, get_all_movies, genres_ids):
    movie_id = get_all_movies[0]["id"]

    res = await ac.patch(f"/v1/movies/{movie_id}", json={"genres_ids": genres_ids})
    assert res.status_code == 200

    updated_movie = await get_and_validate(
        ac=ac,
        url=f"/v1/movies/{movie_id}",
        expect_list=False,
    )

    assert len(updated_movie["genres"]) == len(genres_ids)
    assert all(genre["id"] in genres_ids for genre in updated_movie["genres"])


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "countries_ids",
    [
        [7, 8, 9],
        [2, 3, 7],
        [],
        [1, 2, 3],
        [1],
        [4, 1],
    ],
)
async def test_update_movies_countries(ac, get_all_movies, countries_ids):
    movie_id = get_all_movies[0]["id"]

    res = await ac.patch(f"/v1/movies/{movie_id}", json={"countries_ids": countries_ids})
    assert res.status_code == 200

    updated_movie = await get_and_validate(
        ac=ac,
        url=f"/v1/movies/{movie_id}",
        expect_list=False,
    )

    assert len(updated_movie["countries"]) == len(countries_ids)
    assert all(country["id"] in countries_ids for country in updated_movie["countries"])


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "field,value",
    [
        ("title", "t"),
        ("title", "t" * 257),
        ("description", "d"),
        ("description", "d" * 1025),
        ("release_date", "999-07-07"),
        ("release_date", "2100-07-07"),
        ("duration", 0),
        ("cover_url", "invalid-format"),
        ("video_url", "invalid-format"),
        ("directors_ids", ["invalid-uuid"]),
        ("actors_ids", ["invalid-uuid"]),
        ("genres_ids", [0, 0]),
        ("countries_ids", [0, 0]),
        ("extra", "unknown"),
    ],
)
async def test_update_movie_invalid(ac, get_all_movies, field, value):
    movie_id = get_all_movies[0]["id"]
    res = await ac.patch(f"/v1/movies/{movie_id}", json={field: value})
    assert res.status_code == 422
    assert "detail" in res.json()


@pytest.mark.order(1)
async def test_update_movie_not_found(ac):
    res = await ac.patch(
        url=f"/v1/movies/{uuid7str()}",
        json={"title": "Not Found"},
    )
    assert res.status_code == 404
    assert "detail" in res.json()


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "field, value",
    (
        ("directors_ids", [uuid7str()]),
        ("actors_ids", [uuid7str()]),
        ("genres_ids", [999]),
        ("countries_ids", [999]),
    ),
)
async def test_update_movie_child_not_found(ac, get_all_movies, field, value):
    movie_id = get_all_movies[0]["id"]
    res = await ac.patch(
        url=f"/v1/movies/{movie_id}",
        json={field: value},
    )
    assert res.status_code == 404
    assert "detail" in res.json()


@pytest.mark.order(1)
async def test_update_movie_on_conflict(ac, get_all_movies):
    movie_1, movie_2 = get_all_movies[:2]

    res = await ac.patch(
        url=f"/v1/movies/{movie_1['id']}",
        json={
            "title": movie_2["title"],
            "release_date": movie_2["release_date"],
        },
    )
    assert res.status_code == 409
    assert "detail" in res.json()


@pytest.mark.order(1)
@pytest.mark.parametrize("field", ("cover_url", "video_url"))
async def test_update_movie_on_conflict_urls(ac, get_all_movies, field):
    value = next((m[field] for m in get_all_movies if m[field]), None)
    assert value is not None, f"at least one movie with {field} is required"

    movie_id = next((m["id"] for m in get_all_movies if m[field] != value), None)
    assert movie_id is not None

    res = await ac.patch(
        url=f"/v1/movies/{movie_id}",
        json={field: value},
    )
    assert res.status_code == 409
    assert "detail" in res.json()


@pytest.mark.order(1)
async def test_delete_movie(ac, created_movies):
    for movie in created_movies:
        assert (await ac.get(f"/v1/movies/{movie['id']}")).status_code == 200
        assert (await ac.delete(f"/v1/movies/{movie['id']}")).status_code == 204
        assert (await ac.get(f"/v1/movies/{movie['id']}")).status_code == 404
