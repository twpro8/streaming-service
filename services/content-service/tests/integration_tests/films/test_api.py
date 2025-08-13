from datetime import datetime
from math import ceil

import pytest


films_ids = []


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
    expected_count = sum(1 for film in get_films if title.lower().strip() in film["title"].lower())

    res = await ac.get("/films", params={"title": title, **max_pagination})
    data = res.json()["data"]

    assert res.status_code == 200
    assert isinstance(data, list)
    assert len(data) == expected_count


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
    expected_count = sum(
        1 for film in get_films if director.lower().strip() in film["director"].lower()
    )

    res = await ac.get("/films", params={"director": director, **max_pagination})
    data = res.json()["data"]

    assert res.status_code == 200
    assert isinstance(data, list)
    assert len(data) == expected_count


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
    expected_count = sum(
        1 for film in get_films if description.lower().strip() in film["description"].lower()
    )

    res = await ac.get("/films", params={"description": description, **max_pagination})
    data = res.json()["data"]

    assert res.status_code == 200
    assert isinstance(data, list)
    assert len(data) == expected_count


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
    expected_count = sum(1 for film in get_films if release_year in film["release_year"])

    res = await ac.get("/films", params={"release_year": release_year, **max_pagination})
    data = res.json()["data"]

    assert res.status_code == 200
    assert isinstance(data, list)
    assert len(data) == expected_count


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

    res = await ac.get("/films", params={"release_year_ge": release_year_ge, **max_pagination})
    data = res.json()["data"]

    assert res.status_code == 200
    assert isinstance(data, list)
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

    res = await ac.get("/films", params={"release_year_le": release_year_le, **max_pagination})
    data = res.json()["data"]

    assert res.status_code == 200
    assert isinstance(data, list)
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
    res = await ac.get(
        "/films",
        params={
            "release_year_ge": release_year_ge,
            "release_year_le": release_year_le,
            **max_pagination,
        },
    )
    data = res.json()["data"]

    assert res.status_code == 200
    assert isinstance(data, list)
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

    res = await ac.get("/films", params={"rating": rating, **max_pagination})
    data = res.json()["data"]

    assert res.status_code == 200
    assert isinstance(data, list)
    assert len(data) == expected_count


@pytest.mark.order(1)
@pytest.mark.parametrize("rating_ge", ["0.0", "2.0", "5.0", "9.0"])
async def test_filter_by_rating_ge(ac, rating_ge, get_films, max_pagination):
    expected_count = sum(1 for film in get_films if float(rating_ge) <= float(film["rating"]))

    res = await ac.get("/films", params={"rating_ge": rating_ge, **max_pagination})
    data = res.json()["data"]

    assert res.status_code == 200
    assert isinstance(data, list)
    assert len(data) == expected_count


@pytest.mark.order(1)
@pytest.mark.parametrize("rating_le", ["4.0", "5.0", "9.0"])
async def test_filter_by_rating_le(ac, rating_le, get_films, max_pagination):
    expected_count = sum(1 for film in get_films if float(rating_le) >= float(film["rating"]))

    res = await ac.get("/films", params={"rating_le": rating_le, **max_pagination})
    data = res.json()["data"]

    assert res.status_code == 200
    assert isinstance(data, list)
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

    res = await ac.get("/films", params={"genres_ids": genres_ids, **max_pagination})
    data = res.json()["data"]

    assert res.status_code == 200
    assert isinstance(data, list)
    assert len(data) == expected_count


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "title, description, director, release_year, duration, cover_url, genres_ids, status_code",
    [
        # Valid data
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "2005-01-01",
            140,
            "https://example.com/valid_url.jpg",
            None,
            201,
        ),
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "1999-09-09",
            140,
            None,
            None,
            201,
        ),
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "1969-01-01",
            140,
            "https://ott.com/valid_url.jpg",
            list(range(1, 4)),
            201,
        ),
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "1969-01-01",
            140,
            None,
            list(range(3, 6)),
            201,
        ),
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "1969-01-01",
            140,
            "https://sent.com/valid_url.jpg",
            list(range(5, 11)),
            201,
        ),
        # Invalid title
        ("", "Valid Description", "Valid Director", "2006-01-01", 140, None, None, 422),
        ("T" * 256, "Valid Description", "Valid Director", "2006-01-01", 140, None, None, 422),
        # Invalid description
        ("Valid Title", "", "Valid Director", "2020-01-01", 140, None, None, 422),
        ("Valid Title", "D" * 256, "Valid Director", "2020-01-01", 140, None, None, 422),
        # Invalid director
        ("Valid Title", "Valid Description", "", "2020-01-01", 140, None, None, 422),
        ("Valid Title", "Valid Description", "D" * 50, "2020-01-01", 140, None, None, 422),
        # Invalid release year
        ("Valid Title", "Valid Description", "Valid Director", "10-01-01", 90, None, None, 422),
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "some-garbage-here",
            90,
            None,
            None,
            422,
        ),
        ("Valid Title", "Valid Description", "Valid Director", 1, 90, None, None, 422),
        ("Valid Title", "Description", "Director", "2100-01-01", 90, None, None, 422),
        ("Valid Title", "Description", "Director", "999-01-01", 90, None, None, 422),
        # Invalid duration
        ("Valid Title", "Valid Description", "Valid Director", "2020-01-01", -1, None, None, 422),
        ("Valid Title", "Valid Description", "Valid Director", "2020-01-01", 513, None, None, 422),
        # Invalid cover url
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "2020-01-01",
            140,
            "not-a-url",
            None,
            422,
        ),
        ("Valid Title", "Valid Description", "Valid Director", "2020-01-01", 140, 1, None, 422),
        # All optional fields None (cover_url) - should succeed
        ("Valid Title", "Valid Description", "Valid Director", "2020-01-01", 140, None, None, 201),
        # Conflict
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "2020-01-01",
            140,
            "https://example.com/valid_url.jpg",
            None,
            409,
        ),
        # Genre not found: 404
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "1969-01-01",
            140,
            "https://ett.com/valid_url.jpg",
            [11, 12, 13],
            404,
        ),
        # Invalid genres ids
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "1969-01-01",
            140,
            None,
            ["abs"],
            422,
        ),
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "1969-01-01",
            140,
            None,
            [0, 0],
            422,
        ),
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "1969-01-01",
            140,
            None,
            [-1],
            422,
        ),
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "1969-01-01",
            140,
            None,
            [6.2, 7.3],
            422,
        ),
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "1969-01-01",
            140,
            None,
            [True, False],
            422,
        ),
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "1969-01-01",
            140,
            None,
            [
                [],
            ],
            422,
        ),
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "1969-01-01",
            140,
            None,
            [
                {},
            ],
            422,
        ),
    ],
)
async def test_add_film(
    ac,
    title,
    description,
    director,
    release_year,
    duration,
    cover_url,
    genres_ids,
    status_code,
):
    request_json = {
        "title": title,
        "description": description,
        "director": director,
        "release_year": release_year,
        "duration": duration,
        "cover_url": cover_url,
        "genres_ids": genres_ids,
    }

    res = await ac.post("/films", json=request_json)
    assert res.status_code == status_code

    if status_code == 201:
        film_id = res.json()["data"]["id"]

        res = await ac.get(f"/films/{film_id}")
        film = res.json()["data"]

        assert film["title"] == title
        assert film["description"] == description
        assert film["director"] == director
        assert film["release_year"] == release_year
        assert film["duration"] == duration
        assert film["cover_url"] == cover_url

        if genres_ids is not None:
            assert len(film["genres"]) == len(genres_ids)

        films_ids.append(film_id)


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "update_data, status_code, film_id",
    [
        # Update title
        ({"title": "Title Updated"}, 200, "2449c8d3-6875-467e-b192-e89dc7a5a7e9"),
        ({"title": "Title Updated"}, 200, None),
        # Invalid title
        ({"title": ""}, 422, None),
        ({"title": "T" * 256}, 422, None),
        # Update description
        ({"description": "Description Updated"}, 200, "2449c8d3-6875-467e-b192-e89dc7a5a7e9"),
        ({"description": "Description Updated"}, 200, None),
        # Update genres
        ({"genres_ids": list(range(1, 4))}, 200, None),
        ({"genres_ids": list(range(2, 5))}, 200, None),
        ({"genres_ids": []}, 200, None),
        ({"genres_ids": list(range(4, 7))}, 200, "2449c8d3-6875-467e-b192-e89dc7a5a7e9"),
        ({"genres_ids": list(range(8, 11))}, 200, "2449c8d3-6875-467e-b192-e89dc7a5a7e9"),
        ({"genres_ids": []}, 200, "2449c8d3-6875-467e-b192-e89dc7a5a7e9"),
        ({"genres_ids": [5]}, 200, None),
        ({"genres_ids": [5, 7, 8]}, 200, None),
        ({"genres_ids": []}, 200, None),
        # Invalid description
        ({"description": ""}, 422, None),
        ({"description": "D" * 256}, 422, None),
        # Update director
        ({"director": "Director Updated"}, 200, "2449c8d3-6875-467e-b192-e89dc7a5a7e9"),
        ({"director": "Director Updated"}, 200, None),
        # Invalid director
        ({"director": ""}, 422, None),
        ({"director": "D" * 50}, 422, None),
        # Update release year
        ({"release_year": "2021-01-01"}, 200, "2449c8d3-6875-467e-b192-e89dc7a5a7e9"),
        ({"release_year": "2021-01-01"}, 200, None),
        # Invalid release year
        ({"release_year": "10-01-01"}, 422, None),
        ({"release_year": ""}, 422, None),
        ({"release_year": 1}, 422, None),
        ({"release_year": "2100-01-01"}, 422, None),  # future year
        ({"release_year": "999-01-01"}, 422, None),  # too old
        # Update duration
        ({"duration": 120}, 200, "2449c8d3-6875-467e-b192-e89dc7a5a7e9"),
        ({"duration": 120}, 200, None),
        # Invalid duration
        ({"duration": -1}, 422, None),
        ({"duration": 513}, 422, None),
        # Update cover_url
        (
            {"cover_url": "https://example.com/updated.jpg"},
            200,
            "2449c8d3-6875-467e-b192-e89dc7a5a7e9",
        ),
        ({"cover_url": "https://example.com/updated.jpg"}, 409, None),  # conflict
        # Invalid cover url
        ({"cover_url": ""}, 422, None),
        ({"cover_url": "invalid-uri"}, 422, None),
        # Update video url
        (
            {"video_url": "https://www.youtube.com/watch?v=vGVeDm4118Q"},
            200,
            "2449c8d3-6875-467e-b192-e89dc7a5a7e9",
        ),
        ({"video_url": "https://www.youtube.com/watch?v=vGVeDm4118Q"}, 409, None),  # conflict
        # Invalid video url
        ({"video_url": ""}, 422, None),
        ({"video_url": "invalid-uri"}, 422, None),
        # Update multiple fields
        (
            {"title": "New Title", "description": "New Description", "director": "New Director"},
            200,
            "2449c8d3-6875-467e-b192-e89dc7a5a7e9",
        ),
        (
            {"title": "New Title", "description": "New Description", "director": "New Director"},
            200,
            None,
        ),
        (
            {
                "duration": 99,
                "release_year": "2022-01-01",
                "cover_url": "https://example.com/test.jpg",
            },
            200,
            "2449c8d3-6875-467e-b192-e89dc7a5a7e9",
        ),
        (
            {
                "duration": 99,
                "release_year": "2022-01-01",
                "cover_url": "https://example.com/test.jpg",
            },
            409,
            None,
        ),  # conflict
        # Invalid genres ids
        ({"genres_ids": ["abc"]}, 422, None),
        ({"genres_ids": ["1", "2"]}, 422, None),
        ({"genres_ids": [True, False]}, 422, None),
        ({"genres_ids": [11, 12]}, 404, None),
        ({"genres_ids": [9.1, 8.7]}, 422, None),
    ],
)
async def test_update_film(
    ac,
    update_data,
    status_code,
    film_id,
):
    film_id = film_id or films_ids[0]
    res = await ac.patch(f"/films/{film_id}", json=update_data)
    assert res.status_code == status_code

    if res.status_code == 200:
        res = await ac.get(f"/films/{film_id}")
        data = res.json()["data"]

        for key, value in update_data.items():
            if key == "genres_ids":
                assert len(data["genres"]) == len(value)
            else:
                assert data[key] == value


@pytest.mark.order(1)
async def test_delete_film(ac):
    for film_id in films_ids:
        assert (await ac.get(f"/films/{film_id}")).status_code == 200
        assert (await ac.delete(f"/films/{film_id}")).status_code == 204
        assert (await ac.get(f"/films/{film_id}")).status_code == 404
