from datetime import datetime
from math import ceil

import pytest

from tests.utils import get_and_validate, count_films


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
async def test_films_pagination(ac, page, per_page, max_pagination):
    res = await ac.get("/films", params=max_pagination)
    assert res.status_code == 200

    all_data = res.json()["data"]
    total_count = len(all_data)

    res = await ac.get("/films", params={"page": page, "per_page": per_page})
    assert res.status_code == 200

    data = res.json()["data"]

    total_pages = ceil(total_count / per_page)

    if page <= total_pages:
        expected_length = min(per_page, total_count - (page - 1) * per_page)
    else:
        expected_length = 0

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
    data = await get_and_validate(ac=ac, url="/films", params={"director": director, **max_pagination})
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
    data = await get_and_validate(ac=ac, url="/films", params={"description": description, **max_pagination})
    assert len(data) == count_films(films=get_films, field="description", value=description)


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "release_year",
    [
        "2000-01-01",
        "2003-01-01",
        "2004-01-01",
        "1999-01-01",
    ],
)
async def test_filter_by_exact_release_year(ac, release_year, get_films, max_pagination):
    data = await get_and_validate(ac=ac, url="/films", params={"release_year": release_year, **max_pagination})
    assert len(data) == count_films(films=get_films, field="release_year", value=release_year)


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "release_year_ge",
    [
        "1899-01-01",
        "2003-01-01",
        "2010-01-01",
        "2100-01-01",
    ],
)
async def test_filter_by_release_year_ge(ac, release_year_ge, get_films, max_pagination):
    expected_count = sum(
        1
        for film in get_films
        if datetime.strptime(film["release_year"], "%Y-%m-%d")
        >= datetime.strptime(release_year_ge, "%Y-%m-%d")
    )

    data = await get_and_validate(
        ac=ac,
        url="/films",
        params={
            "release_year_ge": release_year_ge,
            **max_pagination,
        }
    )
    assert len(data) == expected_count


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "release_year_le",
    [
        "1999-01-01",
        "2003-01-01",
        "2005-01-01",
        "2010-01-01",
    ],
)
async def test_filter_by_release_year_le(ac, release_year_le, get_films, max_pagination):
    expected_count = sum(
        1
        for film in get_films
        if datetime.strptime(film["release_year"], "%Y-%m-%d")
        <= datetime.strptime(release_year_le, "%Y-%m-%d")
    )

    data = await get_and_validate(
        ac=ac,
        url="/films",
        params={
            "release_year_le": release_year_le,
            **max_pagination,
        }
    )
    assert len(data) == expected_count


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "release_year_ge, release_year_le",
    [
        ("2002-01-01", "2004-01-01"),
        ("1956-01-01", "2025-01-01"),
        ("1899-01-01", "1952-01-01"),
    ],
)
async def test_filter_by_release_year_range(
    ac, release_year_ge, release_year_le, get_films, max_pagination
):
    expected_count = sum(
        1
        for film in get_films
        if datetime.strptime(release_year_ge, "%Y-%m-%d")
        <= datetime.strptime(film["release_year"], "%Y-%m-%d")
        <= datetime.strptime(release_year_le, "%Y-%m-%d")
    )
    data = await get_and_validate(
        ac=ac,
        url="/films",
        params={
            "release_year_ge": release_year_ge,
            "release_year_le": release_year_le,
            **max_pagination,
        }
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
    data = await get_and_validate(ac=ac, url="/films", params={"rating_ge": rating_ge, **max_pagination})
    assert len(data) == expected_count


@pytest.mark.order(1)
@pytest.mark.parametrize("rating_le", ["4.0", "5.0", "9.0"])
async def test_filter_by_rating_le(ac, rating_le, get_films, max_pagination):
    expected_count = sum(1 for film in get_films if float(rating_le) >= float(film["rating"]))
    data = await get_and_validate(ac=ac, url="/films", params={"rating_le": rating_le, **max_pagination})
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
    data = await get_and_validate(ac=ac, url="/films", params={"genres_ids": genres_ids, **max_pagination})
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
    "title, description, director, release_year, duration, cover_url, genres_ids",
    [
        (
            "Valid Title3",
            "Valid Description3",
            "Valid Director3",
            "2007-01-01",
            135,
            "https://www.example.com/abc",
            [1, 2, 3],
        ),
        (
            "Valid Title4",
            "Valid Description4",
            "Valid Director4",
            "2008-01-01",
            135,
            "https://www.example.com/def",
            [3, 4, 5],
        ),
    ],
)
async def test_add_valid_data_with_optional(
    ac, title, description, director, release_year, duration, cover_url, genres_ids
):
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
async def test_not_found(ac):
    req_body = {
        "title": "Valid Title8",
        "description": "Valid Description8",
        "director": "Valid Director8",
        "release_year": "2020-01-01",
        "duration": 135,
        "cover_url": "https://www.example.com/barbara",
        "genres_ids": [99],  # no such a genre
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
        ("genres_ids", [7, 8, 9]),
        ("genres_ids", [2, 3, 7]),
        ("genres_ids", []),
    ],
)
async def test_update_field_valid(ac, get_films, field, value):
    film_id = get_films[0]["id"]

    res = await ac.patch(f"/films/{film_id}", json={field: value})
    assert res.status_code == 200

    res = await ac.get(f"/films/{film_id}")
    assert res.status_code == 200
    data = res.json()["data"]
    if field == "genres_ids":
        assert len(data["genres"]) == len(value)
        assert all(genre["id"] in value for genre in data["genres"])
    else:
        assert data[field] == value


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
