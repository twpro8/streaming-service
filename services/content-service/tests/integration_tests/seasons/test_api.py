import pytest


seasons_ids = []


@pytest.mark.parametrize(
    "params, target_length",
    [
        ({}, 2),
        ({"page": 1, "per_page": 1}, 1),
        ({"page": 2, "per_page": 1}, 1),
        ({"page": 3, "per_page": 1}, 0),
    ],
)
async def test_get_seasons(ac, get_series_ids, params, target_length):
    for series_id in get_series_ids:
        params = {"series_id": series_id, **params}
        res = await ac.get(
            "/seasons",
            params=params,
        )
        data = res.json()["data"]

        assert res.status_code == 200
        assert isinstance(data, list)
        assert len(data) == target_length


@pytest.mark.parametrize(
    "title, season_number, status_code, series_id",
    [
        # Valid data
        ("Valid Title", 10, 201, "ef66e5c2-0931-4c43-bb6d-bb2b2ec3c9c4"),
        ("Valid Title", 10, 201, None),
        ("Valid Title", 11, 201, "ef66e5c2-0931-4c43-bb6d-bb2b2ec3c9c4"),
        ("Valid Title", 11, 201, None),
        ("Valid Title", 12, 201, "ef66e5c2-0931-4c43-bb6d-bb2b2ec3c9c4"),
        ("Valid Title", 12, 201, None),
        # Invalid title
        (1, 2, 422, None),
        ("", 2, 422, None),
        ("T" * 256, 1, 422, None),
        # Invalid season number
        ("Valid Title", 0, 422, None),
        ("Valid Title", -3, 422, None),
        ("Valid Title", 501, 422, None),
        # Conflict
        ("Valid Title", 10, 409, None),
        ("Valid Title", 11, 409, None),
    ],
)
async def test_add_season(
    ac,
    get_series_ids,
    series_id,
    title,
    season_number,
    status_code,
):
    series_id = series_id or "bf5315e1-fdfc-4af3-b18c-1ccc83892797"
    request_json = {
        "series_id": series_id,
        "title": title,
        "season_number": season_number,
    }

    res = await ac.post("/seasons", json=request_json)
    assert res.status_code == status_code

    if res.status_code == 201:
        seasons_ids.append(res.json()["data"]["id"])


@pytest.mark.parametrize(
    "patch_data, status_code, season_id",
    [
        # Valid data
        ({"title": "Title Updated"}, 200, "abb704d5-da18-4d6a-942e-58f1b6172109"),
        ({"title": "Title Updated"}, 200, None),
        ({"season_number": 42}, 200, "abb704d5-da18-4d6a-942e-58f1b6172109"),
        ({"season_number": 42}, 200, None),
        (
            {"title": "Title Again Updated", "season_number": 99},
            200,
            "abb704d5-da18-4d6a-942e-58f1b6172109",
        ),
        ({"title": "Title Again Updated", "season_number": 99}, 200, None),
        # Invalid title
        ({"title": 1}, 422, None),
        ({"title": ""}, 422, None),
        ({"title": "T" * 256}, 422, None),
        # Invalid season number
        ({"season_number": -1}, 422, None),
        ({"season_number": 501}, 422, None),
        # Empty body
        ({}, 422, None),
        # Conflict
        ({"season_number": 99}, 409, "81c29ee1-db3e-4d81-a257-d05e29773deb"),
        ({"season_number": 99}, 409, "99edd9cc-cd08-4a9d-8809-93b86ab06d28"),
    ],
)
async def test_update_season(ac, patch_data, status_code, season_id):
    season_id = season_id or "d5ed6e69-5d07-474f-81e4-86627a576d45"
    res = await ac.patch(f"/seasons/{season_id}", json=patch_data)
    assert res.status_code == status_code


async def test_delete_season(ac):
    for season_id in seasons_ids:
        assert (await ac.get(f"/seasons/{season_id}")).status_code == 200
        assert (await ac.delete(f"/seasons/{season_id}")).status_code == 204
        assert (await ac.get(f"/seasons/{season_id}")).status_code == 404
