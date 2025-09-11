from itertools import islice

import pytest
from uuid_extensions import uuid7str

from tests.utils import calculate_expected_length, get_and_validate, count_content


@pytest.mark.order(2)
async def test_pagination(ac, get_all_shows):
    per_page = 2
    for page in range(1, 10):
        data = await get_and_validate(
            ac=ac,
            url="/v1/shows",
            params={
                "page": page,
                "per_page": per_page,
            },
        )
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
        ("created_at", "asc"),
        ("created_at", "desc"),
        ("updated_at", "asc"),
        ("updated_at", "desc"),
    ],
)
async def test_show_sorting(ac, field, order, max_pagination):
    data = await get_and_validate(
        ac=ac,
        url="/v1/shows",
        params={
            "sort": f"{field}:{order}",
            **max_pagination,
        },
    )
    # Extract field values for sorting
    if field == "year":
        values = [int(show["release_date"][:4]) for show in data]
    elif field == "id":
        values = [show["id"] for show in data]
    elif field == "rating":
        values = [float(show["rating"]) for show in data]
    elif field == "title":
        values = [show["title"] for show in data]
    elif field == "created_at":
        values = [show["created_at"] for show in data]
    elif field == "updated_at":
        values = [show["updated_at"] for show in data]
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
    data = await get_and_validate(
        ac=ac,
        url="/v1/shows",
        params={
            "title": title,
            **max_pagination,
        },
    )
    expected_content = count_content(get_all_shows, field="title", value=title)
    assert len(data) == expected_content


@pytest.mark.order(2)
@pytest.mark.parametrize("year", [1899, 1995, 2000, 2003, 2004, 2012])
async def test_filter_by_exact_release_year(ac, year, get_all_shows, max_pagination):
    expected_count = sum(1 for show in get_all_shows if year == int(show["release_date"][:4]))
    data = await get_and_validate(
        ac=ac,
        url="/v1/shows",
        params={
            "year": year,
            **max_pagination,
        },
    )
    assert len(data) == expected_count


@pytest.mark.order(2)
@pytest.mark.parametrize("year_gt", [1899, 2002, 2005, 2012])
async def test_filter_by_release_year_gt(ac, year_gt, get_all_shows, max_pagination):
    expected_count = sum(1 for show in get_all_shows if year_gt < int(show["release_date"][:4]))
    data = await get_and_validate(
        ac=ac,
        url="/v1/shows",
        params={
            "year_gt": year_gt,
            **max_pagination,
        },
    )
    assert len(data) == expected_count


@pytest.mark.order(2)
@pytest.mark.parametrize("year_lt", [1899, 2002, 2006, 2012])
async def test_filter_by_release_year_lt(ac, year_lt, get_all_shows, max_pagination):
    expected_count = sum(1 for show in get_all_shows if year_lt > int(show["release_date"][:4]))
    data = await get_and_validate(
        ac=ac,
        url="/v1/shows",
        params={
            "year_lt": year_lt,
            **max_pagination,
        },
    )
    assert len(data) == expected_count


@pytest.mark.order(2)
@pytest.mark.parametrize("year_gt, year_lt", [(2001, 2005), (1899, 2000), (2003, 2012)])
async def test_filter_by_release_year_range(ac, year_gt, year_lt, get_all_shows, max_pagination):
    expected_count = sum(
        1 for show in get_all_shows if year_gt < int(show["release_date"][:4]) < year_lt
    )
    data = await get_and_validate(
        ac=ac,
        url="/v1/shows",
        params={
            "year_gt": year_gt,
            "year_lt": year_lt,
            **max_pagination,
        },
    )
    assert len(data) == expected_count


@pytest.mark.order(2)
@pytest.mark.parametrize("rating", [0.0, 1.0, 5.0, 7.5, 8.0, 2.0])
async def test_filter_by_rating(ac, rating, get_all_shows, max_pagination):
    expected_count = sum(1 for show in get_all_shows if rating == float(show["rating"]))
    data = await get_and_validate(
        ac=ac,
        url="/v1/shows",
        params={
            "rating": rating,
            **max_pagination,
        },
    )
    assert len(data) == expected_count


@pytest.mark.order(2)
@pytest.mark.parametrize("rating_gt", [0.0, 1.0, 5.0, 7.5, 8.0, 2.0])
async def test_filter_by_rating_gt(ac, rating_gt, get_all_shows, max_pagination):
    expected_count = sum(1 for show in get_all_shows if rating_gt < float(show["rating"]))
    data = await get_and_validate(
        ac=ac,
        url="/v1/shows",
        params={
            "rating_gt": rating_gt,
            **max_pagination,
        },
    )
    assert len(data) == expected_count


@pytest.mark.order(2)
@pytest.mark.parametrize("rating_lt", [0.0, 5.0, 1.0, 5.0, 7.5, 8.0, 2.0])
async def test_filter_by_rating_lt(ac, rating_lt, get_all_shows, max_pagination):
    expected_count = sum(1 for show in get_all_shows if rating_lt > float(show["rating"]))
    data = await get_and_validate(
        ac=ac,
        url="/v1/shows",
        params={
            "rating_lt": rating_lt,
            **max_pagination,
        },
    )
    assert len(data) == expected_count


@pytest.mark.order(2)
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
async def test_filter_by_rating_range(ac, rating_gt, rating_lt, get_all_shows, max_pagination):
    expected_count = sum(
        1 for show in get_all_shows if rating_gt < float(show["rating"]) < rating_lt
    )
    data = await get_and_validate(
        ac=ac,
        url="/v1/shows",
        params={
            "rating_gt": rating_gt,
            "rating_lt": rating_lt,
            **max_pagination,
        },
    )
    assert len(data) == expected_count


@pytest.mark.order(2)
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
    get_all_shows_with_rels,
    max_pagination,
):
    directors_ids = [get_all_directors[i]["id"] for i in set_indexes]
    expected_count = sum(
        1
        for show in get_all_shows_with_rels
        if any(director["id"] in directors_ids for director in show["directors"])
    )
    data = await get_and_validate(
        ac=ac,
        url="/v1/shows",
        params={
            "directors_ids": directors_ids,
            **max_pagination,
        },
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
    actors_ids = [get_all_actors[i]["id"] for i in set_indexes]
    expected_count = sum(
        1
        for show in get_all_shows_with_rels
        if any(actor["id"] in actors_ids for actor in show["actors"])
    )
    data = await get_and_validate(
        ac=ac,
        url="/v1/shows",
        params={
            "actors_ids": actors_ids,
            **max_pagination,
        },
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
        ac=ac,
        url="/v1/shows",
        params={
            "genres_ids": genres_ids,
            **max_pagination,
        },
    )
    assert len(data) == expected_count


@pytest.mark.order(2)
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
async def test_get_filter_by_countries(ac, countries_ids, get_all_shows_with_rels, max_pagination):
    expected_count = sum(
        1
        for show in get_all_shows_with_rels
        if any(country["id"] in countries_ids for country in show["countries"])
    )
    data = await get_and_validate(
        ac=ac,
        url="/v1/shows",
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
    res = await ac.get("/v1/shows", params={field: value})
    assert res.status_code == 422
    assert "detail" in res.json()


@pytest.mark.order(2)
async def test_get_show(ac, get_all_shows):
    for show in islice(get_all_shows, 2):
        data = await get_and_validate(
            ac=ac,
            url=f"/v1/shows/{show['id']}",
            expect_list=False,
        )
        assert isinstance(data, dict)
        assert data["id"] == show["id"]
        assert data["title"] == show["title"]
        assert data["description"] == show["description"]
        assert data["release_date"] == show["release_date"]
        assert data["rating"] == show["rating"]
        assert data["cover_url"] == show["cover_url"]
        assert data["created_at"] == show["created_at"]
        assert data["updated_at"] == show["updated_at"]


@pytest.mark.order(2)
async def test_get_show_not_found(ac):
    res = await ac.get(url=f"/v1/shows/{uuid7str()}")
    assert res.status_code == 404
    assert "detail" in res.json()


@pytest.mark.order(2)
@pytest.mark.parametrize(
    "title, description, release_date",
    [
        (
            "Valid Title",
            "Valid Description",
            "2005-01-01",
        ),
        (
            "Valid Title2",
            "Valid Description2",
            "2006-01-01",
        ),
    ],
)
async def test_add_show_without_optional_valid(ac, title, description, release_date):
    res = await ac.post(
        "/v1/shows",
        json={
            "title": title,
            "description": description,
            "release_date": release_date,
        },
    )
    assert res.status_code == 201

    show_id = res.json()["data"]["id"]
    added_show = await get_and_validate(
        ac=ac,
        url=f"/v1/shows/{show_id}",
        expect_list=False,
    )

    assert added_show["title"] == title
    assert added_show["description"] == description
    assert added_show["release_date"] == release_date
    assert "rating" in added_show
    assert added_show["created_at"]
    assert added_show["updated_at"]


@pytest.mark.order(2)
@pytest.mark.parametrize(
    """
    title, 
    description, 
    release_date, 
    cover_url, 
    directors_indexes,
    actors_indexes,
    genres_ids,
    countries_ids
    """,
    [
        (
            "Valid Title3",
            "Valid Description",
            "2005-01-01",
            "https://www.example.com/abc",
            [0, 1, 2],
            [0, 1, 2],
            [1, 2, 3],
            [1, 2, 3],
        ),
        (
            "Valid Title4",
            "Valid Description2",
            "2006-01-01",
            "https://www.example.com/def",
            [2, 3, 4],
            [2, 3, 4],
            [3, 4, 5],
            [3, 4, 5],
        ),
    ],
)
async def test_add_show_with_optional_valid(
    ac,
    get_all_directors,
    get_all_actors,
    title,
    description,
    release_date,
    cover_url,
    directors_indexes,
    actors_indexes,
    genres_ids,
    countries_ids,
):
    directors_ids = [get_all_directors[i]["id"] for i in directors_indexes]
    actors_ids = [get_all_actors[i]["id"] for i in actors_indexes]
    res = await ac.post(
        "/v1/shows",
        json={
            "title": title,
            "description": description,
            "release_date": release_date,
            "cover_url": cover_url,
            "directors_ids": directors_ids,
            "actors_ids": actors_ids,
            "countries_ids": countries_ids,
            "genres_ids": genres_ids,
        },
    )
    assert res.status_code == 201

    show_id = res.json()["data"]["id"]
    added_show = await get_and_validate(
        ac=ac,
        url=f"/v1/shows/{show_id}",
        expect_list=False,
    )

    assert added_show["title"] == title
    assert added_show["description"] == description
    assert added_show["release_date"] == release_date
    assert added_show["cover_url"] == cover_url

    assert len(added_show["directors"]) == len(directors_ids)
    assert len(added_show["actors"]) == len(actors_ids)
    assert len(added_show["genres"]) == len(genres_ids)
    assert len(added_show["countries"]) == len(countries_ids)

    assert all(director["id"] in directors_ids for director in added_show["directors"])
    assert all(actor["id"] in actors_ids for actor in added_show["actors"])
    assert all(genre["id"] in genres_ids for genre in added_show["genres"])
    assert all(country["id"] in countries_ids for country in added_show["countries"])

    assert "rating" in added_show
    assert added_show["created_at"]
    assert added_show["updated_at"]


@pytest.mark.order(2)
@pytest.mark.parametrize(
    "field, value",
    (
        ("title", "t"),
        ("title", "t" * 257),
        ("description", "d"),
        ("description", "d" * 1025),
        ("release_date", "999-01-01"),
        ("release_date", "2100-01-01"),
        ("cover_url", "invalid-url"),
        ("directors_ids", ["invalid-uuid"]),
        ("actors_ids", ["invalid-uuid"]),
        ("genres_ids", [0, 0]),
        ("countries_ids", [0, 0]),
        ("extra", "unknown"),
    ),
)
async def test_add_show_invalid(ac, field, value):
    valid_data = {
        "title": "Valid Title3",
        "description": "Valid Description3",
        "release_date": "2012-01-01",
        "cover_url": "https://www.example.com/meaw/cat.png",
        field: value,
    }
    res = await ac.post("/v1/shows", json=valid_data)
    assert res.status_code == 422
    assert "detail" in res.json()


@pytest.mark.order(2)
async def test_add_show_on_conflict(ac, get_all_shows):
    for show in islice(get_all_shows, 2):
        res = await ac.post(
            url="/v1/shows",
            json={
                "title": show["title"],
                "description": "Some description",
                "release_date": show["release_date"],
            },
        )
        assert res.status_code == 409
        assert "detail" in res.json()


@pytest.mark.order(2)
async def test_add_show_on_conflict_cover_url(ac, get_all_shows):
    cover_url = next((s["cover_url"] for s in get_all_shows if s["cover_url"]), None)
    assert cover_url is not None, "at least one show with cover url is required"

    res = await ac.post(
        url="/v1/shows",
        json={
            "title": "valid title for conflict test",
            "description": "valid description for conflict test",
            "release_date": "1988-01-01",
            "cover_url": cover_url,
        },
    )
    assert res.status_code == 409
    assert "detail" in res.json()


@pytest.mark.order(2)
@pytest.mark.parametrize(
    "field, value",
    [
        ("directors_ids", [uuid7str()]),
        ("actors_ids", [uuid7str()]),
        ("genres_ids", [999]),
        ("countries_ids", [999]),
    ],
)
async def test_add_show_not_found(ac, field, value):
    req_body = {
        "title": "Valid Title8",
        "description": "Valid Description8",
        "release_date": "2020-01-01",
        "cover_url": "https://www.example.com/barbara",
        field: value,
    }
    res = await ac.post("/v1/shows", json=req_body)
    assert res.status_code == 404
    assert "detail" in res.json()


@pytest.mark.order(2)
@pytest.mark.parametrize(
    "field,value",
    [
        ("title", "Title Updated 1"),
        ("title", "Title Updated 2"),
        ("description", "Description Updated 1"),
        ("description", "Description Updated 2"),
        ("release_date", "1888-01-01"),
        ("release_date", "1999-07-07"),
        ("cover_url", f"https://{uuid7str()}/pic.jpg"),
        ("cover_url", None),
    ],
)
async def test_update_field_valid(ac, get_all_shows, field, value):
    show = get_all_shows[0]

    res = await ac.patch(f"/v1/shows/{show['id']}", json={field: value})
    assert res.status_code == 200

    updated_show = await get_and_validate(
        ac=ac,
        url=f"/v1/shows/{show['id']}",
        expect_list=False,
    )
    assert isinstance(updated_show, dict)
    assert updated_show["id"] == show["id"]
    assert updated_show[field] == value

    unchanged_fields = (
        "title",
        "description",
        "release_date",
        "cover_url",
    )
    for f in unchanged_fields:
        if f != field:
            assert updated_show[f] == show[f]

    assert updated_show["rating"] == show["rating"]
    assert updated_show["created_at"] == show["created_at"]
    assert updated_show["updated_at"] != show["updated_at"]


@pytest.mark.order(2)
@pytest.mark.parametrize(
    "directors_indexes", [[0, 1, 2], [2, 3], [], [5, 7, 9], [0, 4, 2], [], [7, 8, 1]]
)
async def test_update_show_directors(ac, get_all_directors, get_all_shows, directors_indexes):
    show_id = get_all_shows[0]["id"]
    directors_ids = [get_all_directors[i]["id"] for i in directors_indexes]

    res = await ac.patch(f"/v1/shows/{show_id}", json={"directors_ids": directors_ids})
    assert res.status_code == 200

    updated_show = await get_and_validate(
        ac=ac,
        url=f"/v1/shows/{show_id}",
        expect_list=False,
    )

    assert len(updated_show["directors"]) == len(directors_indexes)
    assert all(director["id"] in directors_ids for director in updated_show["directors"])


@pytest.mark.order(2)
@pytest.mark.parametrize(
    "actors_indexes", [[0, 1, 2], [2, 3], [], [5, 7, 9], [0, 4, 2], [], [7, 8, 1]]
)
async def test_update_show_actors(ac, get_all_actors, get_all_shows, actors_indexes):
    show_id = get_all_shows[0]["id"]
    actors_ids = [get_all_actors[i]["id"] for i in actors_indexes]

    res = await ac.patch(f"/v1/shows/{show_id}", json={"actors_ids": actors_ids})
    assert res.status_code == 200

    updated_show = await get_and_validate(
        ac=ac,
        url=f"/v1/shows/{show_id}",
        expect_list=False,
    )

    assert len(updated_show["actors"]) == len(actors_indexes)
    assert all(actor["id"] in actors_ids for actor in updated_show["actors"])


@pytest.mark.order(2)
@pytest.mark.parametrize("genres_ids", [[7, 8, 9], [2, 3, 7], [], [1, 2, 3]])
async def test_update_show_genres(ac, get_all_shows, genres_ids):
    show_id = get_all_shows[0]["id"]

    res = await ac.patch(f"/v1/shows/{show_id}", json={"genres_ids": genres_ids})
    assert res.status_code == 200

    updated_show = await get_and_validate(
        ac=ac,
        url=f"/v1/shows/{show_id}",
        expect_list=False,
    )

    assert len(updated_show["genres"]) == len(genres_ids)
    assert all(genre["id"] in genres_ids for genre in updated_show["genres"])


@pytest.mark.order(2)
@pytest.mark.parametrize("countries_ids", [[7, 8, 9], [2, 3, 7], [], [1, 2, 3]])
async def test_update_show_countries(ac, get_all_shows, countries_ids):
    show_id = get_all_shows[0]["id"]

    res = await ac.patch(f"/v1/shows/{show_id}", json={"countries_ids": countries_ids})
    assert res.status_code == 200

    updated_show = await get_and_validate(
        ac=ac,
        url=f"/v1/shows/{show_id}",
        expect_list=False,
    )

    assert len(updated_show["countries"]) == len(countries_ids)
    assert all(country["id"] in countries_ids for country in updated_show["countries"])


@pytest.mark.order(2)
@pytest.mark.parametrize(
    "field,value",
    [
        ("title", "t"),
        ("title", "t" * 257),
        ("description", "d"),
        ("description", "d" * 1025),
        ("release_date", "999-07-07"),
        ("release_date", "2100-07-07"),
        ("cover_url", "invalid-format"),
        ("directors_ids", ["invalid-uuid"]),
        ("actors_ids", ["invalid-uuid"]),
        ("genres_ids", [0, 0]),
        ("countries_ids", [0, 0]),
        ("extra", "unknown"),
    ],
)
async def test_update_show_invalid(ac, get_all_shows, field, value):
    show_id = get_all_shows[0]["id"]
    res = await ac.patch(f"/v1/shows/{show_id}", json={field: value})
    assert res.status_code == 422
    assert "detail" in res.json()


@pytest.mark.order(2)
async def test_update_show_not_found(ac):
    res = await ac.patch(
        url=f"/v1/shows/{uuid7str()}",
        json={"title": "Not Found"},
    )
    assert res.status_code == 404
    assert "detail" in res.json()


@pytest.mark.order(2)
@pytest.mark.parametrize(
    "field, value",
    (
        ("directors_ids", [uuid7str()]),
        ("actors_ids", [uuid7str()]),
        ("genres_ids", [999]),
        ("countries_ids", [999]),
    ),
)
async def test_update_show_child_not_found(ac, get_all_shows, field, value):
    show_id = get_all_shows[0]["id"]
    res = await ac.patch(
        url=f"/v1/shows/{show_id}",
        json={field: value},
    )
    assert res.status_code == 404
    assert "detail" in res.json()


@pytest.mark.order(2)
async def test_update_show_on_conflict(ac, get_all_shows):
    show_1, show_2 = get_all_shows[:2]

    res = await ac.patch(
        url=f"/v1/shows/{show_1['id']}",
        json={
            "title": show_2["title"],
            "release_date": show_2["release_date"],
        },
    )
    assert res.status_code == 409
    assert "detail" in res.json()


@pytest.mark.order(2)
async def test_update_show_on_conflict_cover_url(ac, get_all_shows):
    value = next((s["cover_url"] for s in get_all_shows if s["cover_url"]), None)
    assert value is not None, "at least one show with cover_url is required"

    show_id = next((s["id"] for s in get_all_shows if s["cover_url"] != value), None)
    assert value is not None

    res = await ac.patch(
        url=f"/v1/shows/{show_id}",
        json={"cover_url": value},
    )
    assert res.status_code == 409
    assert "detail" in res.json()


@pytest.mark.order(2)
async def test_delete_show(ac, created_shows):
    for show in created_shows:
        assert (await ac.get(f"/v1/shows/{show['id']}")).status_code == 200
        assert (await ac.delete(f"/v1/shows/{show['id']}")).status_code == 204
        assert (await ac.get(f"/v1/shows/{show['id']}")).status_code == 404
