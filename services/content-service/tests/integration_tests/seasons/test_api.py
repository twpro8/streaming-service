import pytest


series_seasons_data = {}


def add_season(series_id: str, season_id: str):
    series_seasons_data.setdefault(series_id, [])
    if season_id not in series_seasons_data[series_id]:
        series_seasons_data[series_id].append(season_id)


@pytest.mark.parametrize(
    "title, season_number, status_code",
    [
        # Valid data
        ("Season One", 1, 201),
        ("Season Two", 2, 201),
        ("Final Season", 10, 201),
        ("Mini Season", 500, 201),
        ("Low Bound", 3, 201),
        # Existing season nimber
        ("Low Bound", 3, 409),
        # Invalid: season_number too high
        ("Too Many", 501, 422),
        # Invalid: season_number zero
        ("Zero Season", 0, 422),
        # Invalid: season_number negative
        ("Negative Season", -3, 422),
        # Invalid: empty title
        ("", 2, 422),
        # Invalid: title too long
        ("S" * 256, 1, 422),
    ],
)
async def test_add_season(
    ac,
    get_series_ids,
    title,
    season_number,
    status_code,
):
    for series_id in get_series_ids:
        request_json = {
            "title": title,
            "season_number": season_number,
        }

        res = await ac.post(f"/series/{series_id}/seasons", json=request_json)
        assert res.status_code == status_code

        if res.status_code == 201:
            season_id = res.json()["data"]["id"]
            add_season(series_id, season_id)


async def test_get_seasons(ac, get_series_ids):
    for series_id in get_series_ids:
        res = await ac.get(
            f"/series/{series_id}/seasons",
            params={"page": 1, "per_page": 30},
        )
        data = res.json()["data"]

        assert res.status_code == 200
        assert isinstance(data, list)
        assert len(data) == 5


@pytest.mark.parametrize(
    "patch_data, expected_status",
    [
        # valid updates
        ({"title": "Updated Season Title"}, 200),
        ({"season_number": 42}, 200),
        ({"title": "Combined", "season_number": 99}, 200),
        # same data (still allowed)
        ({"title": "Season One"}, 200),
        # invalid title
        ({"title": ""}, 422),
        ({"title": "S" * 256}, 422),
        # invalid season_number
        ({"season_number": 0}, 422),
        ({"season_number": 501}, 422),
        ({"season_number": -10}, 422),
        # empty body
        ({}, 422),
    ],
)
async def test_update_season(ac, patch_data, expected_status):
    for series_id, season_ids in series_seasons_data.items():
        res = await ac.patch(
            f"/series/{series_id}/seasons/{season_ids[-1]}",
            json=patch_data,
        )
        assert res.status_code == expected_status

        if expected_status == 200:
            assert res.json()["status"] == "ok"


async def test_delete_season(ac):
    for series_id, season_ids in series_seasons_data.items():
        for season_id in season_ids:
            res = await ac.delete(
                f"/series/{series_id}/seasons/{season_id}",
            )
            assert res.status_code == 204

            res = await ac.get(f"/series/{series_id}/seasons/{season_id}")
            assert res.status_code == 404

        res = await ac.get(f"/series/{series_id}/seasons")
        assert res.status_code == 200
        assert len(res.json()["data"]) == 0
