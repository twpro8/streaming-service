from uuid import uuid4

import pytest

from tests.utils import get_and_validate, count_films, calculate_expected_length


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "page, per_page",
    [
        (1, 2),
        (2, 2),
        (3, 2),
        (4, 2),
    ],
)
async def test_films_pagination(ac, page, per_page, get_all_films):
    res = await ac.get("/films", params={"page": page, "per_page": per_page})
    assert res.status_code == 200
    data = res.json()["data"]
    expected_length = calculate_expected_length(page, per_page, len(get_all_films))
    assert len(data) == expected_length


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
async def test_filter_by_title_valid(ac, title, get_films, max_pagination):
    data = await get_and_validate(ac=ac, url="/films", params={"title": title, **max_pagination})
    assert len(data) == count_films(films=get_films, field="title", value=title)


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "director",
    [
        " GRETA Thorn ",
        "   Guy   ",
        "   Quantum",
        "Lens   ",
        "   Max",
        "no match",
        "who is he?",
        "Some guy",
    ],
)
async def test_filter_by_director(ac, director, get_films, max_pagination):
    data = await get_and_validate(
        ac=ac, url="/films", params={"director": director, **max_pagination}
    )
    assert len(data) == count_films(films=get_films, field="director", value=director)


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "description",
    [
        "    the ",
        "about isolation",
        "post-apocalyptic wasteland",
        "and",
        "no match",
        "unknown desc",
        "funky drive",
    ],
)
async def test_filter_by_description(ac, description, get_films, max_pagination):
    data = await get_and_validate(
        ac=ac, url="/films", params={"description": description, **max_pagination}
    )
    assert len(data) == count_films(films=get_films, field="description", value=description)


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "year",
    [
        2000,
        2003,
        2004,
        1999,
    ],
)
async def test_filter_by_exact_release_year(ac, year, get_films, max_pagination):
    data = await get_and_validate(ac=ac, url="/films", params={"year": year, **max_pagination})
    expected_count = sum(1 for film in get_films if year == int(film["release_year"][:4]))
    assert len(data) == expected_count


@pytest.mark.order(1)
@pytest.mark.parametrize("year_gt", [1899, 2003, 2010, 2100])
async def test_filter_by_release_year_gt(ac, year_gt, get_films, max_pagination):
    expected_count = sum(1 for film in get_films if int(film["release_year"][:4]) > year_gt)

    data = await get_and_validate(
        ac=ac,
        url="/films",
        params={
            "year_gt": year_gt,
            **max_pagination,
        },
    )
    assert len(data) == expected_count


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "year_lt",
    [1999, 2003, 2005, 2010],
)
async def test_filter_by_release_year_lt(ac, year_lt, get_films, max_pagination):
    expected_count = sum(1 for film in get_films if int(film["release_year"][:4]) < year_lt)

    data = await get_and_validate(
        ac=ac,
        url="/films",
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
    get_films,
    max_pagination,
):
    expected_count = sum(
        1 for film in get_films if year_gt < int(film["release_year"][:4]) < year_lt
    )
    data = await get_and_validate(
        ac=ac,
        url="/films",
        params={
            "year_gt": year_gt,
            "year_lt": year_lt,
            **max_pagination,
        },
    )
    assert len(data) == expected_count


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "rating",
    [
        "0.0",
        "1.0",
        "5.0",
        "7.0",
        "8.0",
    ],
)
async def test_filter_by_exact_rating(ac, rating, get_films, max_pagination):
    expected_count = sum(1 for film in get_films if rating in film["rating"])
    data = await get_and_validate(ac=ac, url="/films", params={"rating": rating, **max_pagination})
    assert len(data) == expected_count


@pytest.mark.order(1)
@pytest.mark.parametrize("rating_ge", ["0.0", "2.0", "5.0", "9.0"])
async def test_filter_by_rating_ge(ac, rating_ge, get_films, max_pagination):
    expected_count = sum(1 for film in get_films if float(rating_ge) <= float(film["rating"]))
    data = await get_and_validate(
        ac=ac, url="/films", params={"rating_ge": rating_ge, **max_pagination}
    )
    assert len(data) == expected_count


@pytest.mark.order(1)
@pytest.mark.parametrize("rating_le", ["4.0", "5.0", "9.0"])
async def test_filter_by_rating_le(ac, rating_le, get_films, max_pagination):
    expected_count = sum(1 for film in get_films if float(rating_le) >= float(film["rating"]))
    data = await get_and_validate(
        ac=ac, url="/films", params={"rating_le": rating_le, **max_pagination}
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
async def test_get_filter_by_genres(ac, genres_ids, get_films_with_rels, max_pagination):
    expected_count = sum(
        1
        for film in get_films_with_rels
        if any(genre["id"] in genres_ids for genre in film["genres"])
    )
    data = await get_and_validate(
        ac=ac, url="/films", params={"genres_ids": genres_ids, **max_pagination}
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
    get_films_with_rels,
    max_pagination,
):
    actors_ids = [str(get_all_actors[i]["id"]) for i in set_indexes]
    expected_count = sum(
        1
        for film in get_films_with_rels
        if any(actor["id"] in actors_ids for actor in film["actors"])
    )
    data = await get_and_validate(ac, "/films", params={"actors_ids": actors_ids, **max_pagination})
    assert len(data) == expected_count


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "title, description, director, release_year, duration",
    [
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "2005-01-01",
            140,
        ),
        (
            "Valid Title2",
            "Valid Description2",
            "Valid Director2",
            "2006-01-01",
            135,
        ),
    ],
)
async def test_add_valid_data_without_optional(
    ac, title, description, director, release_year, duration
):
    res = await ac.post(
        "/films",
        json={
            "title": title,
            "description": description,
            "director": director,
            "release_year": release_year,
            "duration": duration,
        },
    )
    assert res.status_code == 201

    film_id = res.json()["data"]["id"]
    film = await get_and_validate(ac=ac, url=f"/films/{film_id}", expect_list=False)

    assert film["title"] == title
    assert film["description"] == description
    assert film["director"] == director
    assert film["release_year"] == release_year
    assert film["duration"] == duration


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "title, description, director, release_year, duration, cover_url, genres_ids, actors_indexes",
    [
        (
            "Valid Title3",
            "Valid Description3",
            "Valid Director3",
            "2007-01-01",
            135,
            "https://www.example.com/abc",
            [1, 2, 3],
            [0, 1, 2],
        ),
        (
            "Valid Title4",
            "Valid Description4",
            "Valid Director4",
            "2008-01-01",
            135,
            "https://www.example.com/def",
            [3, 4, 5],
            [2, 3, 4],
        ),
    ],
)
async def test_add_valid_data_with_optional(
    ac,
    title,
    description,
    director,
    release_year,
    duration,
    cover_url,
    genres_ids,
    actors_indexes,
    get_all_actors,
):
    actors_ids = [str(get_all_actors[i]["id"]) for i in actors_indexes]
    res = await ac.post(
        "/films",
        json={
            "title": title,
            "description": description,
            "director": director,
            "release_year": release_year,
            "duration": duration,
            "cover_url": cover_url,
            "genres_ids": genres_ids,
            "actors_ids": actors_ids,
        },
    )
    assert res.status_code == 201

    film_id = res.json()["data"]["id"]

    film = await get_and_validate(ac=ac, url=f"/films/{film_id}", expect_list=False)

    assert film["title"] == title
    assert film["description"] == description
    assert film["director"] == director
    assert film["release_year"] == release_year
    assert film["duration"] == duration
    assert film["cover_url"] == cover_url
    assert len(film["genres"]) == len(genres_ids)
    assert all(genre["id"] in genres_ids for genre in film["genres"])


invalid_cases = [
    ("title", [None, True, False, "t", "t" * 256, 1, [], {}, 1.1]),
    ("description", [None, True, False, "d", "d" * 256, 1, [], {}, 1.1]),
    ("director", [None, True, False, "d", "d" * 50, 1, [], {}, 1.1]),
    (
        "release_year",
        ["10-01-01", "999-01-01", "2100-01-01", None, True, False, "string", 1, [], {}, 1.1],
    ),
    ("duration", [None, False, -1, 513, "string", [], {}, 1.1]),
    ("cover_url", ["string", False, [], {}, 0, 1, 1.1]),
    ("genres_ids", ["string", False, {}, 0, 1, 1.1, ["string", 1.1, False, 0, [], {}]]),
    ("actors_ids", ["string", 11]),
]


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "field, invalid_value", [(field, val) for field, vals in invalid_cases for val in vals]
)
async def test_add_invalid_fields(ac, field, invalid_value):
    valid_data = {
        "title": "Valid Title5",
        "description": "Valid Description5",
        "director": "Valid Director5",
        "release_year": "2020-01-01",
        "duration": 135,
        "cover_url": "https://www.example.com/me/image.png",
        "genres_ids": [7, 8, 9],
        field: invalid_value,
    }
    res = await ac.post("/films", json=valid_data)
    assert res.status_code == 422
    assert "detail" in res.json()


@pytest.mark.order(1)
async def test_on_conflict(ac, get_films_with_rels):
    req_body = {
        "title": "Valid Title7",
        "description": "Valid Description7",
        "director": "Valid Director7",
        "release_year": "2020-01-01",
        "duration": 135,
        "cover_url": "https://www.example.com/me/image.png",  # unique
        "genres_ids": [7, 8, 9],
    }
    res = await ac.post("/films", json=req_body)
    assert res.status_code == 201

    res = await ac.post("/films", json=req_body)
    assert res.status_code == 409


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "field, value",
    [
        ("genres_ids", [99]),
        ("actors_ids", [str(uuid4())]),
    ],
)
async def test_not_found(ac, field, value):
    req_body = {
        "title": "Valid Title8",
        "description": "Valid Description8",
        "director": "Valid Director8",
        "release_year": "2020-01-01",
        "duration": 135,
        "cover_url": "https://www.example.com/barbara",
        field: value,
    }
    res = await ac.post("/films", json=req_body)
    assert res.status_code == 404


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "field,value",
    [
        ("title", "Title Updated 1"),
        ("title", "Title Updated 2"),
        ("description", "Description Updated 1"),
        ("description", "Description Updated 2"),
        ("director", "Director Updated 1"),
        ("director", "Director Updated 2"),
        ("release_year", "1888-01-01"),
        ("release_year", "1999-07-07"),
        ("duration", 111),
        ("duration", 222),
        ("duration", 333),
        ("cover_url", "https://example.com/updated.jpg"),
    ],
)
async def test_update_field_valid(ac, get_films, field, value):
    film_id = get_films[0]["id"]

    res = await ac.patch(f"/films/{film_id}", json={field: value})
    assert res.status_code == 200

    data = await get_and_validate(ac, f"/films/{film_id}", expect_list=False)
    assert data[field] == value


@pytest.mark.order(1)
@pytest.mark.parametrize("genres_ids", [[7, 8, 9], [2, 3, 7], [], [1, 2, 3]])
async def test_update_films_genres(ac, get_films, genres_ids):
    film_id = get_films[0]["id"]

    res = await ac.patch(f"/films/{film_id}", json={"genres_ids": genres_ids})
    assert res.status_code == 200

    data = await get_and_validate(ac, f"/films/{film_id}", expect_list=False)

    assert len(data["genres"]) == len(genres_ids)
    assert all(genre["id"] in genres_ids for genre in data["genres"])


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "actors_indexes", [[0, 1, 2], [2, 3], [], [5, 7, 9], [0, 4, 2], [], [7, 8, 1]]
)
async def test_update_films_actors(ac, get_all_actors, get_films, actors_indexes):
    film_id = get_films[0]["id"]
    actors_ids = [str(get_all_actors[i]["id"]) for i in actors_indexes]

    res = await ac.patch(f"/films/{film_id}", json={"actors_ids": actors_ids})
    assert res.status_code == 200

    data = await get_and_validate(ac, f"/films/{film_id}", expect_list=False)

    assert len(data["actors"]) == len(actors_indexes)
    assert all(actor["id"] in actors_ids for actor in data["actors"])


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "field,value",
    [
        ("title", "t"),
        ("title", "t" * 256),
        ("title", 11),
        ("description", "d"),
        ("description", "d" * 256),
        ("description", 11),
        ("director", "d"),
        ("director", "d" * 50),
        ("director", 11),
        ("release_year", "10-01-01"),
        ("release_year", "999-07-07"),
        ("release_year", "2100-07-07"),
        ("duration", -1),
        ("duration", 513),
        ("cover_url", "invalid-format"),
        ("genres_ids", 11),
        ("genres_ids", ["str"]),
        ("actors_ids", [11]),
        ("actors_ids", ["str"]),
    ],
)
async def test_update_field_invalid(ac, get_films, field, value):
    film_id = get_films[0]["id"]
    res = await ac.patch(f"/films/{film_id}", json={field: value})
    assert res.status_code == 422
    assert "detail" in res.json()


@pytest.mark.order(1)
async def test_delete_film(ac, created_films):
    for film in created_films:
        assert (await ac.get(f"/films/{film['id']}")).status_code == 200
        assert (await ac.delete(f"/films/{film['id']}")).status_code == 204
        assert (await ac.get(f"/films/{film['id']}")).status_code == 404
