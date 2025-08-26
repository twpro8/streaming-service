from uuid import uuid4

import pytest

from tests.utils import calculate_expected_length, get_and_validate, count_content


@pytest.mark.order(2)
@pytest.mark.parametrize(
    "page, per_page",
    [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (1, 30),
    ],
)
async def test_pagination(ac, page, per_page, get_all_shows):
    data = await get_and_validate(ac, "/v1/shows", params={"page": page, "per_page": per_page})
    expected_length = calculate_expected_length(page, per_page, len(get_all_shows))
    assert len(data) == expected_length


@pytest.mark.order(2)
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
    ],
)
async def test_show_sorting(ac, field, order, max_pagination):
    data = await get_and_validate(
        ac, "/v1/shows", params={"sort": f"{field}:{order}", **max_pagination}
    )
    # Extract field values for sorting
    if field == "year":
        values = [int(show["release_year"][:4]) for show in data]
    elif field == "id":
        values = [show["id"] for show in data]
    elif field == "rating":
        values = [float(show["rating"]) for show in data]
    elif field == "title":
        values = [show["title"] for show in data]
    else:
        raise AssertionError(f"Unknown field: {field}")
    sorted_values = sorted(values, reverse=(order == "desc"))
    assert values == sorted_values


@pytest.mark.order(2)
@pytest.mark.parametrize(
    "title",
    [
        "Bad",
        "Things ",
        " THE ",
        "no match",
        "meet dave",
    ],
)
async def test_filter_by_title(ac, title, get_all_shows, max_pagination):
    data = await get_and_validate(ac, "/v1/shows", params={"title": title, **max_pagination})
    assert len(data) == count_content(get_all_shows, field="title", value=title)


@pytest.mark.order(2)
@pytest.mark.parametrize(
    "director",
    [
        "Johan Renck",
        "The Duffer",
        " THE ",
        "no Guy",
        "dave",
    ],
)
async def test_filter_by_director(ac, director, get_all_shows, max_pagination):
    data = await get_and_validate(ac, "/v1/shows", params={"director": director, **max_pagination})
    assert len(data) == count_content(get_all_shows, field="director", value=director)


@pytest.mark.order(2)
@pytest.mark.parametrize(
    "description",
    [
        "story of the chernobyl",
        "diagnosed with cancer",
        " THE ",
        "nothing",
        "no match",
    ],
)
async def test_filter_by_description(ac, description, get_all_shows, max_pagination):
    data = await get_and_validate(
        ac, "/v1/shows", params={"description": description, **max_pagination}
    )
    assert len(data) == count_content(get_all_shows, field="description", value=description)


@pytest.mark.order(2)
@pytest.mark.parametrize("year", [1899, 1995, 2000, 2003, 2004, 2012])
async def test_filter_by_release_year(ac, year, get_all_shows, max_pagination):
    expected_count = sum(1 for show in get_all_shows if year == show["release_year"].year)
    data = await get_and_validate(ac, "/v1/shows", params={"year": year, **max_pagination})
    assert len(data) == expected_count


@pytest.mark.order(2)
@pytest.mark.parametrize("year_gt", [1899, 2002, 2005, 2012])
async def test_filter_by_release_year_gt(ac, year_gt, get_all_shows, max_pagination):
    expected_count = sum(1 for show in get_all_shows if year_gt < show["release_year"].year)
    data = await get_and_validate(ac, "/v1/shows", params={"year_gt": year_gt, **max_pagination})
    assert len(data) == expected_count


@pytest.mark.order(2)
@pytest.mark.parametrize("year_lt", [1899, 2002, 2006, 2012])
async def test_filter_by_release_year_lt(ac, year_lt, get_all_shows, max_pagination):
    expected_count = sum(1 for show in get_all_shows if year_lt > show["release_year"].year)
    data = await get_and_validate(ac, "/v1/shows", params={"year_lt": year_lt, **max_pagination})
    assert len(data) == expected_count


@pytest.mark.order(2)
@pytest.mark.parametrize("year_gt, year_lt", [(2001, 2005), (1899, 2000), (2003, 2012)])
async def test_filter_by_release_year_range(ac, year_gt, year_lt, get_all_shows, max_pagination):
    expected_count = sum(
        1 for show in get_all_shows if year_gt < show["release_year"].year < year_lt
    )
    data = await get_and_validate(
        ac, "/v1/shows", params={"year_gt": year_gt, "year_lt": year_lt, **max_pagination}
    )
    assert len(data) == expected_count


@pytest.mark.order(2)
@pytest.mark.parametrize("rating", [0.0, 1.0, 5.0, 7.5, 8.0, 2.0])
async def test_filter_by_rating(ac, rating, get_all_shows, max_pagination):
    expected_count = sum(1 for show in get_all_shows if rating == float(show["rating"]))
    data = await get_and_validate(ac, "/v1/shows", params={"rating": rating, **max_pagination})
    assert len(data) == expected_count


@pytest.mark.order(2)
@pytest.mark.parametrize("rating_gt", [0.0, 1.0, 5.0, 7.5, 8.0, 2.0])
async def test_filter_by_rating_gt(ac, rating_gt, get_all_shows, max_pagination):
    expected_count = sum(1 for show in get_all_shows if rating_gt < float(show["rating"]))
    data = await get_and_validate(
        ac, "/v1/shows", params={"rating_gt": rating_gt, **max_pagination}
    )
    assert len(data) == expected_count


@pytest.mark.order(2)
@pytest.mark.parametrize("rating_lt", [0.0, 5.0, 1.0, 5.0, 7.5, 8.0, 2.0])
async def test_filter_by_rating_lt(ac, rating_lt, get_all_shows, max_pagination):
    expected_count = sum(1 for show in get_all_shows if rating_lt > float(show["rating"]))
    data = await get_and_validate(
        ac, "/v1/shows", params={"rating_lt": rating_lt, **max_pagination}
    )
    assert len(data) == expected_count


@pytest.mark.order(2)
@pytest.mark.parametrize(
    "rating_gt, rating_lt", [(0.0, 0.3), (5.0, 7.6), (1.0, 4.5), (5.0, 6.0), (7.5, 9.0)]
)
async def test_filter_by_rating_range(ac, rating_gt, rating_lt, get_all_shows, max_pagination):
    expected_count = sum(
        1 for show in get_all_shows if rating_gt < float(show["rating"]) < rating_lt
    )
    data = await get_and_validate(
        ac, "/v1/shows", params={"rating_gt": rating_gt, "rating_lt": rating_lt, **max_pagination}
    )
    assert len(data) == expected_count


@pytest.mark.order(2)
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
async def test_filter_by_genres(ac, genres_ids, get_all_shows_with_rels, max_pagination):
    expected_count = sum(
        1
        for s in get_all_shows_with_rels
        if any(genre["id"] in genres_ids for genre in s["genres"])
    )
    data = await get_and_validate(
        ac, "/v1/shows", params={"genres_ids": genres_ids, **max_pagination}
    )
    assert len(data) == expected_count


@pytest.mark.order(2)
@pytest.mark.parametrize(
    "set_indexes",
    [
        [0, 1, 2, 3, 4],
        [1, 4],
        [1, 3, 4],
        [1],
        [2],
        [8, 9, 5],
        [4],
    ],
)
async def test_get_filter_by_actors(
    ac,
    set_indexes,
    get_all_actors,
    get_all_shows_with_rels,
    max_pagination,
):
    actors_ids = [str(get_all_actors[i]["id"]) for i in set_indexes]
    expected_count = sum(
        1
        for show in get_all_shows_with_rels
        if any(actor["id"] in actors_ids for actor in show["actors"])
    )
    data = await get_and_validate(
        ac, "/v1/shows", params={"actors_ids": actors_ids, **max_pagination}
    )
    assert len(data) == expected_count


@pytest.mark.order(2)
@pytest.mark.parametrize(
    "title, description, director, release_year",
    [
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "2005-01-01",
        ),
        (
            "Valid Title2",
            "Valid Description2",
            "Valid Director2",
            "2006-01-01",
        ),
    ],
)
async def test_add_show_without_optional_valid(ac, title, description, director, release_year):
    res = await ac.post(
        "/v1/shows",
        json={
            "title": title,
            "description": description,
            "director": director,
            "release_year": release_year,
        },
    )
    assert res.status_code == 201

    show_id = res.json()["data"]["id"]
    show = await get_and_validate(ac=ac, url=f"/v1/shows/{show_id}", expect_list=False)

    assert show["title"] == title
    assert show["description"] == description
    assert show["director"] == director
    assert show["release_year"] == release_year


@pytest.mark.order(2)
@pytest.mark.parametrize(
    "title, description, director, release_year, cover_url, genres_ids, actors_indexes",
    [
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "2005-01-01",
            "https://www.example.com/abc",
            [1, 2, 3],
            [0, 1, 2],
        ),
        (
            "Valid Title2",
            "Valid Description2",
            "Valid Director2",
            "2006-01-01",
            "https://www.example.com/def",
            [3, 4, 5],
            [2, 3, 4],
        ),
    ],
)
async def test_add_show_with_optional_valid(
    ac,
    title,
    description,
    director,
    release_year,
    cover_url,
    genres_ids,
    actors_indexes,
    get_all_actors,
):
    actors_ids = [str(get_all_actors[i]["id"]) for i in actors_indexes]
    res = await ac.post(
        "/v1/shows",
        json={
            "title": title,
            "description": description,
            "director": director,
            "release_year": release_year,
            "cover_url": cover_url,
            "genres_ids": genres_ids,
            "actors_ids": actors_ids,
        },
    )
    assert res.status_code == 201

    show_id = res.json()["data"]["id"]
    show = await get_and_validate(ac=ac, url=f"/v1/shows/{show_id}", expect_list=False)

    assert show["title"] == title
    assert show["description"] == description
    assert show["director"] == director
    assert show["release_year"] == release_year
    assert show["cover_url"] == cover_url
    assert len(show["genres"]) == len(genres_ids)
    assert all(genre["id"] in genres_ids for genre in show["genres"])


invalid_cases = [
    ("title", ["t", "t" * 256]),
    (
        "description",
        [
            "d",
            "d" * 256,
        ],
    ),
    ("director", ["d", "d" * 50]),
    ("release_year", ["10-01-01", "999-01-01", "2100-01-01"]),
    ("cover_url", ["invalid-format"]),
    ("genres_ids", ["string", ["string"]]),
    ("actors_ids", ["string", 11]),
]


@pytest.mark.order(2)
@pytest.mark.parametrize(
    "field, invalid_value", [(field, val) for field, vals in invalid_cases for val in vals]
)
async def test_add_show_invalid(ac, field, invalid_value):
    valid_data = {
        "title": "Valid Title3",
        "description": "Valid Description3",
        "director": "Valid Director3",
        "release_year": "2012-01-01",
        "cover_url": "https://www.example.com/meaw/cat.png",
        "genres_ids": [7, 8, 9],
        "actors_ids": [1, 2, 3],
        field: invalid_value,
    }
    res = await ac.post("/v1/shows", json=valid_data)
    assert res.status_code == 422
    assert "detail" in res.json()


@pytest.mark.order(2)
async def test_show_on_conflict(ac):
    req_body = {
        "title": "Valid Title7",
        "description": "Valid Description7",
        "director": "Valid Director7",
        "release_year": "2020-01-01",
        "cover_url": "https://www.kitten.com/kitty.jpg",  # unique
    }
    res = await ac.post("/v1/shows", json=req_body)
    assert res.status_code == 201

    res = await ac.post("/v1/shows", json=req_body)
    assert res.status_code == 409


@pytest.mark.order(2)
@pytest.mark.parametrize(
    "field, value",
    [
        ("genres_ids", [99]),
        ("actors_ids", [str(uuid4())]),
    ],
)
async def test_show_not_found(ac, field, value):
    req_body = {
        "title": "Valid Title8",
        "description": "Valid Description8",
        "director": "Valid Director8",
        "release_year": "2020-01-01",
        "cover_url": "https://www.example.com/barbara",
        field: value,
    }
    res = await ac.post("/v1/shows", json=req_body)
    assert res.status_code == 404


@pytest.mark.order(2)
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
        ("cover_url", "https://example.com/updated.jpg"),
        ("cover_url", None),
    ],
)
async def test_update_field_valid(ac, get_all_shows, field, value):
    show_id = get_all_shows[0]["id"]

    res = await ac.patch(f"/v1/shows/{show_id}", json={field: value})
    assert res.status_code == 200

    data = await get_and_validate(ac, f"/v1/shows/{show_id}", expect_list=False)
    assert data[field] == value


@pytest.mark.order(2)
@pytest.mark.parametrize("genres_ids", [[7, 8, 9], [2, 3, 7], [], [1, 2, 3]])
async def test_update_show_genres(ac, get_all_shows, genres_ids):
    show_id = get_all_shows[0]["id"]

    res = await ac.patch(f"/v1/shows/{show_id}", json={"genres_ids": genres_ids})
    assert res.status_code == 200

    data = await get_and_validate(ac, f"/v1/shows/{show_id}", expect_list=False)

    assert len(data["genres"]) == len(genres_ids)
    assert all(genre["id"] in genres_ids for genre in data["genres"])


@pytest.mark.order(2)
@pytest.mark.parametrize(
    "actors_indexes", [[0, 1, 2], [2, 3], [], [5, 7, 9], [0, 4, 2], [], [7, 8, 1]]
)
async def test_update_show_actors(ac, get_all_actors, get_all_shows, actors_indexes):
    show_id = get_all_shows[0]["id"]
    actors_ids = [str(get_all_actors[i]["id"]) for i in actors_indexes]

    res = await ac.patch(f"/v1/shows/{show_id}", json={"actors_ids": actors_ids})
    assert res.status_code == 200

    data = await get_and_validate(ac, f"/v1/shows/{show_id}", expect_list=False)

    assert len(data["actors"]) == len(actors_indexes)
    assert all(actor["id"] in actors_ids for actor in data["actors"])


@pytest.mark.order(2)
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
        ("cover_url", "invalid-format"),
        ("genres_ids", 11),
        ("genres_ids", ["str"]),
        ("actors_ids", [11]),
        ("actors_ids", ["str"]),
    ],
)
async def test_update_show_invalid(ac, get_all_shows, field, value):
    show_id = get_all_shows[0]["id"]
    res = await ac.patch(f"/v1/shows/{show_id}", json={field: value})
    assert res.status_code == 422
    assert "detail" in res.json()


@pytest.mark.order(2)
async def test_delete_show(ac, created_shows):
    for show in created_shows:
        assert (await ac.get(f"/v1/shows/{show['id']}")).status_code == 200
        assert (await ac.delete(f"/v1/shows/{show['id']}")).status_code == 204
        assert (await ac.get(f"/v1/shows/{show['id']}")).status_code == 404
