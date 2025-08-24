from uuid import uuid4

import pytest

from tests.utils import calculate_expected_length, get_and_validate


@pytest.mark.parametrize(
    "page, per_page",
    [
        (1, 1),
        (2, 1),
        (3, 1),
        (1, 2),
        (2, 2),
    ],
)
async def test_get_seasons(ac, get_all_series, get_all_seasons, page, per_page):
    for series in get_all_series:
        seasons_in_series_count = sum(
            1 for season in get_all_seasons if season["series_id"] == series["id"]
        )
        expected_count = calculate_expected_length(page, per_page, seasons_in_series_count)
        data = await get_and_validate(
            ac, "/v1/seasons", params={"series_id": series["id"], "page": page, "per_page": per_page}
        )
        assert len(data) == expected_count


@pytest.mark.parametrize(
    "title, season_number",
    [
        ("Valid Season Title 1", 10),
        ("Valid Season Title 2", 11),
    ],
)
async def test_add_season_valid(ac, get_all_series, title, season_number):
    for i in range(2):
        series_id = str(get_all_series[i]["id"])

        res = await ac.post(
            "/v1/seasons",
            json={
                "series_id": series_id,
                "title": title,
                "season_number": season_number,
            },
        )
        assert res.status_code == 201

        season_id = res.json()["data"]["id"]

        season = await get_and_validate(ac, f"/v1/seasons/{season_id}", expect_list=False)
        assert season["title"] == title
        assert season["season_number"] == season_number


@pytest.mark.parametrize(
    "field, value",
    [
        ("title", 12),
        ("title", "t"),
        ("title", "t" * 256),
        ("episode_number", 0),
        ("episode_number", -1),
        ("episode_number", 501),
    ],
)
async def test_add_season_invalid(ac, get_all_series, field, value):
    series_id = str(get_all_series[0]["id"])
    req_body = {
        "series_id": series_id,
        "title": "Valid Season Title 3",
        "episode_number": 12,
        field: value,
    }
    res = await ac.post("/v1/seasons", json=req_body)
    assert res.status_code == 422


@pytest.mark.parametrize("season_number", (10, 11))
async def test_add_season_on_conflict(ac, get_all_series, season_number):
    for i in range(2):
        series_id = str(get_all_series[i]["id"])
        res = await ac.post(
            "/v1/seasons",
            json={
                "series_id": series_id,
                "title": "Valid Season Title 4",
                "season_number": season_number,  # unique season number per series
            },
        )
        assert res.status_code == 409


async def test_add_season_not_found(ac):
    for _ in range(2):
        res = await ac.post(
            "/v1/seasons",
            json={
                "series_id": str(uuid4()),
                "title": "Valid Season Title 5",
                "season_number": 13,
            },
        )
        assert res.status_code == 404


@pytest.mark.parametrize("title", ("Title Updated 1", "Title Updated 2"))
async def test_update_season_title_valid(ac, get_all_seasons, title):
    for i in range(2):
        season_id = str(get_all_seasons[i]["id"])

        res = await ac.patch(f"/v1/seasons/{season_id}", json={"title": title})
        assert res.status_code == 200

        season = await get_and_validate(ac, f"/v1/seasons/{season_id}", expect_list=False)
        assert season["title"] == title


@pytest.mark.parametrize("season_number", (14, 15))
async def test_update_season_number_valid(ac, get_all_series, get_all_seasons, season_number):
    for i in range(2):
        series_id = get_all_series[i]["id"]

        seasons = await get_and_validate(ac, "/v1/seasons", params={"series_id": series_id})
        season_id = seasons[0]["id"]

        res = await ac.patch(f"/v1/seasons/{season_id}", json={"season_number": season_number})
        assert res.status_code == 200

        season = await get_and_validate(ac, f"/v1/seasons/{season_id}", expect_list=False)
        assert season["season_number"] == season_number


@pytest.mark.parametrize(
    "field, value",
    (
        ("title", "t"),
        ("title", "t" * 256),
        ("episode_number", 0),
        ("episode_number", 501),
    ),
)
async def test_update_season_invalid(ac, get_all_seasons, field, value):
    season_id = get_all_seasons[0]["id"]
    res = await ac.patch(f"/v1/seasons/{season_id}", json={field: value})
    assert res.status_code == 422
    assert "detail" in res.json()


async def test_update_season_on_conflict(ac, get_all_series):
    series_id = get_all_series[0]["id"]

    seasons = await get_and_validate(ac, "/v1/seasons", params={"series_id": series_id})

    res = await ac.patch(f"/v1/seasons/{seasons[0]['id']}", json={"season_number": 20})
    assert res.status_code == 200

    res = await ac.patch(f"/v1/seasons/{seasons[1]['id']}", json={"season_number": 20})
    assert res.status_code == 409


async def test_update_season_not_found(ac):
    for _ in range(2):
        res = await ac.patch(f"/v1/seasons/{str(uuid4())}", json={"title": "Valid Season Title 7"})
        assert res.status_code == 404


async def test_delete_season(ac, get_all_seasons):
    for season in get_all_seasons[4:]:
        assert (await ac.get(f"/v1/seasons/{season['id']}")).status_code == 200
        assert (await ac.delete(f"/v1/seasons/{season['id']}")).status_code == 204
        assert (await ac.get(f"/v1/seasons/{season['id']}")).status_code == 404
