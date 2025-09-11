from itertools import islice

import pytest
from uuid_extensions import uuid7str

from tests.utils import (
    calculate_expected_length,
    get_and_validate,
    first_group,
    next_number,
    first_different,
)


async def test_get_seasons(ac, get_all_shows, get_all_seasons):
    per_page = 1
    for page in range(1, 4):
        for show in islice(get_all_shows, 2):
            seasons_in_shows_count = sum(
                1 for season in get_all_seasons if season["show_id"] == show["id"]
            )
            expected_count = calculate_expected_length(
                page=page,
                per_page=per_page,
                total_count=seasons_in_shows_count,
            )
            data = await get_and_validate(
                ac=ac,
                url="/v1/seasons",
                params={
                    "show_id": show["id"],
                    "page": page,
                    "per_page": per_page,
                },
            )
            assert len(data) == expected_count


async def test_get_season(ac, get_all_seasons):
    for season in islice(get_all_seasons, 2):
        data = await get_and_validate(
            ac=ac,
            url=f"/v1/seasons/{season['id']}",
            expect_list=False,
        )
        assert isinstance(data, dict)
        assert data["id"] == season["id"]
        assert data["show_id"] == season["show_id"]
        assert data["title"] == season["title"]
        assert data["season_number"] == season["season_number"]
        assert data["created_at"] == season["created_at"]
        assert data["updated_at"] == season["updated_at"]


async def test_get_season_not_found(ac):
    res = await ac.get(url=f"/v1/seasons/{uuid7str()}")
    assert res.status_code == 404
    assert "detail" in res.json()


@pytest.mark.parametrize(
    "title, season_number",
    [
        ("Valid Season Title 1", 10),
        ("Valid Season Title 2", 11),
    ],
)
async def test_add_season_valid(ac, get_all_shows, title, season_number):
    for i in range(2):
        show_id = get_all_shows[i]["id"]

        res = await ac.post(
            "/v1/seasons",
            json={
                "show_id": show_id,
                "title": title,
                "season_number": season_number,
            },
        )
        assert res.status_code == 201

        season_id = res.json()["data"]["id"]
        added_season = await get_and_validate(
            ac=ac,
            url=f"/v1/seasons/{season_id}",
            expect_list=False,
        )

        assert added_season["id"] == season_id
        assert added_season["show_id"] == show_id
        assert added_season["title"] == title
        assert added_season["season_number"] == season_number
        assert added_season["created_at"]
        assert added_season["updated_at"]


@pytest.mark.parametrize(
    "field, value",
    [
        ("title", "t"),
        ("title", "t" * 257),
        ("season_number", 0),
        ("extra", "unknown"),
    ],
)
async def test_add_season_invalid(ac, get_all_shows, field, value):
    show_id = get_all_shows[0]["id"]
    req_body = {
        "show_id": show_id,
        "title": "Valid Season Title 3",
        "season_number": 12,
        field: value,
    }
    res = await ac.post("/v1/seasons", json=req_body)
    assert res.status_code == 422
    assert "detail" in res.json()


async def test_add_season_on_conflict(ac, get_all_seasons):
    season = get_all_seasons[0]

    res = await ac.post(
        "/v1/seasons",
        json={
            "show_id": season["show_id"],
            "title": season["title"],
            "season_number": season["season_number"],
        },
    )
    assert res.status_code == 409
    assert "detail" in res.json()


async def test_add_season_show_not_found(ac, get_all_seasons):
    res = await ac.post(
        "/v1/seasons",
        json={
            "show_id": uuid7str(),
            "title": "Valid Season Title",
            "season_number": 1,
        },
    )
    assert res.status_code == 404


@pytest.mark.parametrize("title", ("Title Updated 1", "Title Updated 2"))
async def test_update_season_title_valid(ac, get_all_seasons, title):
    for i in range(2):
        season = get_all_seasons[i]

        res = await ac.patch(
            url=f"/v1/seasons/{season['id']}",
            json={"title": title},
        )
        assert res.status_code == 200

        updated_season = await get_and_validate(
            ac=ac,
            url=f"/v1/seasons/{season['id']}",
            expect_list=False,
        )
        assert updated_season["id"] == season["id"]
        assert updated_season["show_id"] == season["show_id"]
        assert updated_season["title"] == title
        assert updated_season["season_number"] == season["season_number"]
        assert updated_season["created_at"] == season["created_at"]
        assert updated_season["updated_at"] != season["updated_at"]


async def test_update_season_number_valid(ac, get_all_seasons):
    seasons = first_different(get_all_seasons, "show_id", 2)
    uq_season_num = next_number(get_all_seasons, "season_number")

    for season in seasons:
        res = await ac.patch(
            url=f"/v1/seasons/{season['id']}",
            json={"season_number": uq_season_num},
        )
        assert res.status_code == 200

        updated_season = await get_and_validate(
            ac=ac,
            url=f"/v1/seasons/{season['id']}",
            expect_list=False,
        )
        assert updated_season["id"] == season["id"]
        assert updated_season["show_id"] == season["show_id"]
        assert updated_season["title"] == season["title"]
        assert updated_season["season_number"] == uq_season_num
        assert updated_season["created_at"] == season["created_at"]
        assert updated_season["updated_at"] != season["updated_at"]


@pytest.mark.parametrize(
    "field, value",
    (
        ("title", "t"),
        ("title", "t" * 257),
        ("season_number", 0),
        ("extra", "unknown"),
    ),
)
async def test_update_season_invalid(ac, get_all_seasons, field, value):
    season_id = get_all_seasons[0]["id"]
    res = await ac.patch(f"/v1/seasons/{season_id}", json={field: value})
    assert res.status_code == 422
    assert "detail" in res.json()


async def test_update_season_on_conflict(ac, get_all_seasons):
    season_1, season_2 = first_group(items=get_all_seasons, group_by="show_id", n=2)

    res = await ac.patch(
        url=f"/v1/seasons/{season_1['id']}",
        json={"season_number": season_2["season_number"]},
    )
    assert res.status_code == 409
    assert "detail" in res.json()


async def test_update_season_not_found(ac):
    res = await ac.patch(
        url=f"/v1/seasons/{uuid7str()}",
        json={"title": "Valid Season Title 8"},
    )
    assert res.status_code == 404
    assert "detail" in res.json()


async def test_delete_season(ac, get_all_seasons):
    for season in islice(get_all_seasons, 2):
        assert (await ac.get(f"/v1/seasons/{season['id']}")).status_code == 200
        assert (await ac.delete(f"/v1/seasons/{season['id']}")).status_code == 204
        assert (await ac.get(f"/v1/seasons/{season['id']}")).status_code == 404
