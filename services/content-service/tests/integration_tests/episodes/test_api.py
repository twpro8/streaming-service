from itertools import islice

import pytest
from uuid_extensions import uuid7str

from tests.utils import (
    calculate_expected_length,
    get_and_validate,
    first_group,
    next_number,
)


async def test_episode_pagination(ac, get_all_episodes):
    per_page = 3
    for page in range(1, 8):
        expected_count = calculate_expected_length(
            page=page,
            per_page=per_page,
            total_count=len(get_all_episodes),
        )
        episodes = await get_and_validate(
            ac=ac,
            url="/v1/episodes",
            params={
                "page": page,
                "per_page": per_page,
            },
        )
        assert len(episodes) == expected_count


async def test_get_filter_by_show_id(ac, get_all_shows, max_pagination):
    for show in islice(get_all_shows, 2):
        show_id = show["id"]
        episodes = await get_and_validate(
            ac=ac,
            url="/v1/episodes",
            params={
                "show_id": show_id,
                **max_pagination,
            },
        )
        expected_count = sum(1 for ep in episodes if ep["show_id"] == show_id)
        assert len(episodes) == expected_count


async def test_get_filter_by_season_id(ac, get_all_seasons, max_pagination):
    for season in islice(get_all_seasons, 4):
        season_id = season["id"]
        episodes = await get_and_validate(
            ac=ac,
            url="/v1/episodes",
            params={
                "season_id": season_id,
                **max_pagination,
            },
        )
        expected_count = sum(1 for ep in episodes if ep["season_id"] == season_id)
        assert len(episodes) == expected_count


@pytest.mark.parametrize("episode_number", (1, 2, 3))
async def test_get_filter_by_episode_number(ac, get_all_episodes, episode_number, max_pagination):
    episodes = await get_and_validate(
        ac=ac,
        url="/v1/episodes",
        params={
            "episode_number": episode_number,
            **max_pagination,
        },
    )
    expected_count = sum(1 for ep in get_all_episodes if ep["episode_number"] == episode_number)
    assert len(episodes) == expected_count


async def test_get_empty_result(ac, get_all_shows):
    show_id = get_all_shows[0]["id"]
    res = await ac.get(
        "/v1/episodes",
        params={
            "show_id": show_id,
            "season_id": uuid7str(),
        },
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.parametrize("field", ("show_id", "season_id", "episode_number"))
async def test_invalid_query_params(ac, field):
    res = await ac.get("/v1/episodes", params={field: "invalid"})
    assert res.status_code == 422
    assert "detail" in res.json()


async def test_get_episode(ac, get_all_episodes):
    for ep in islice(get_all_episodes, 2):
        data = await get_and_validate(
            ac=ac,
            url=f"/v1/episodes/{ep['id']}",
            expect_list=False,
        )
        assert isinstance(data, dict)
        assert ep["id"] == data["id"]
        assert ep["show_id"] == data["show_id"]
        assert ep["season_id"] == data["season_id"]
        assert ep["title"] == data["title"]
        assert ep["episode_number"] == data["episode_number"]
        assert ep["created_at"] == data["created_at"]
        assert ep["updated_at"] == data["updated_at"]


async def test_get_episode_not_found(ac):
    res = await ac.get(f"/v1/episodes/{uuid7str()}")
    assert res.status_code == 404
    assert "detail" in res.json()


@pytest.mark.parametrize("episode_number", (10, 11))
async def test_add_episode_valid(ac, get_all_seasons, episode_number):
    for i in range(2):
        show_id = get_all_seasons[i]["show_id"]
        season_id = get_all_seasons[i]["id"]

        req_body = {
            "show_id": show_id,
            "season_id": season_id,
            "title": "valid episode title",
            "episode_number": episode_number,
            "duration": 77,
            "video_url": f"https://{uuid7str()}/video.avi",
        }
        res = await ac.post("/v1/episodes", json=req_body)
        assert res.status_code == 201

        episode_id = res.json()["data"]["id"]
        added_episode = await get_and_validate(
            ac=ac,
            url=f"/v1/episodes/{episode_id}",
            expect_list=False,
        )
        assert added_episode["id"] == episode_id
        assert added_episode["show_id"] == show_id
        assert added_episode["title"] == req_body["title"]
        assert added_episode["episode_number"] == episode_number
        assert added_episode["duration"] == req_body["duration"]
        assert added_episode["video_url"] == req_body["video_url"]
        assert added_episode["created_at"]
        assert added_episode["updated_at"]


@pytest.mark.parametrize(
    "field, value",
    [
        ("title", "t"),
        ("title", "t" * 257),
        ("episode_number", 0),
        ("duration", 0),
        ("video_url", "invalid-format"),
        ("extra", "unknown"),
    ],
)
async def test_add_episode_invalid(ac, get_all_seasons, field, value):
    show_id = get_all_seasons[0]["show_id"]
    season_id = get_all_seasons[0]["id"]

    res = await ac.post(
        "/v1/episodes",
        json={
            "show_id": show_id,
            "season_id": season_id,
            "title": "Valid Episode Title 3",
            "episode_number": 14,
            "duration": 77,
            "video_url": f"https://{uuid7str()}/video.mp4",
            field: value,
        },
    )
    assert res.status_code == 422
    assert "detail" in res.json()


async def test_add_episode_on_conflict_ep_number(ac, get_all_episodes):
    existing_ep = get_all_episodes[0]

    res = await ac.post(
        url="/v1/episodes",
        json={
            "show_id": existing_ep["show_id"],
            "season_id": existing_ep["season_id"],
            "title": "Valid Title",
            "episode_number": existing_ep["episode_number"],
            "duration": 77,
        },
    )
    assert res.status_code == 409
    assert "detail" in res.json()


async def test_add_episode_on_conflict_video_url(ac, get_all_episodes):
    existing_ep = next((ep for ep in get_all_episodes if ep["video_url"]), None)
    assert existing_ep is not None, "at least one episode with video url is required"

    ep_num = next_number(
        get_all_episodes,
        "episode_number",
        lambda e: e["season_id"] == existing_ep["season_id"],
    )

    res = await ac.post(
        url="/v1/episodes",
        json={
            "show_id": existing_ep["show_id"],
            "season_id": existing_ep["season_id"],
            "title": "Valid Title",
            "episode_number": ep_num,
            "duration": 77,
            "video_url": existing_ep["video_url"],
        },
    )
    assert res.status_code == 409
    assert "detail" in res.json()


@pytest.mark.parametrize("case", ("show", "season"))
async def test_add_episode_not_found(ac, get_all_episodes, case):
    episode = get_all_episodes[0]

    show_id = uuid7str() if case == "show" else episode["show_id"]
    season_id = uuid7str() if case == "season" else episode["season_id"]

    res = await ac.post(
        "/v1/episodes",
        json={
            "show_id": show_id,
            "season_id": season_id,
            "title": "Valid Title",
            "episode_number": 1,
            "duration": 77,
        },
    )
    assert res.status_code == 404
    assert "detail" in res.json()


@pytest.mark.parametrize(
    "field, value",
    [
        ("title", "Title Updated"),
        ("duration", 80),
        ("video_url", f"https://{uuid7str()}/video.avi"),
        ("video_url", None),
    ],
)
async def test_update_episode_valid(ac, get_all_episodes, field, value):
    episode = get_all_episodes[0]

    res = await ac.patch(f"/v1/episodes/{episode['id']}", json={field: value})
    assert res.status_code == 200

    updated_episode = await get_and_validate(
        ac=ac,
        url=f"/v1/episodes/{episode['id']}",
        expect_list=False,
    )
    assert updated_episode["id"] == episode["id"]
    assert updated_episode["show_id"] == episode["show_id"]
    assert updated_episode["season_id"] == episode["season_id"]
    assert updated_episode["episode_number"] == episode["episode_number"]
    assert updated_episode[field] == value

    unchanged_fields = ("title", "duration", "video_url")
    for f in unchanged_fields:
        if f != field:
            assert updated_episode[f] == episode[f]

    assert updated_episode["created_at"] == episode["created_at"]
    assert updated_episode["updated_at"] != episode["updated_at"]


async def test_update_episode_number(ac, get_all_episodes):
    episode = get_all_episodes[1]

    ep_num = next_number(
        get_all_episodes,
        "episode_number",
        lambda e: e["season_id"] == episode["season_id"],
    )

    res = await ac.patch(f"/v1/episodes/{episode['id']}", json={"episode_number": ep_num})
    assert res.status_code == 200

    updated_episode = await get_and_validate(
        ac=ac,
        url=f"/v1/episodes/{episode['id']}",
        expect_list=False,
    )
    assert updated_episode["id"] == episode["id"]
    assert updated_episode["show_id"] == episode["show_id"]
    assert updated_episode["season_id"] == episode["season_id"]
    assert updated_episode["title"] == episode["title"]
    assert updated_episode["episode_number"] == ep_num
    assert updated_episode["duration"] == episode["duration"]
    assert updated_episode["video_url"] == episode["video_url"]
    assert updated_episode["created_at"] == episode["created_at"]
    assert updated_episode["updated_at"] != episode["updated_at"]


@pytest.mark.parametrize(
    "field, value",
    [
        ("title", "t"),
        ("title", "t" * 257),
        ("episode_number", 0),
        ("duration", 0),
        ("video_url", "invalid-format"),
        ("extra", "unknown"),
    ],
)
async def test_update_episode_invalid(ac, get_all_episodes, field, value):
    episode_id = get_all_episodes[0]["id"]
    res = await ac.patch(f"/v1/episodes/{episode_id}", json={field: value})
    assert res.status_code == 422
    assert "detail" in res.json()


@pytest.mark.parametrize(
    "field, value",
    [
        ("episode_number", 5),
        ("video_url", f"https://{uuid7str()}/video.avi"),
    ],
)
async def test_update_episode_on_conflict(ac, get_all_episodes, field, value):
    episodes = first_group(get_all_episodes, "season_id", 2)

    if field == "episode_number":
        value = next_number(episodes, "episode_number")

    res = await ac.patch(f"/v1/episodes/{episodes[0]['id']}", json={field: value})
    assert res.status_code == 200

    res = await ac.patch(f"/v1/episodes/{episodes[1]['id']}", json={field: value})
    assert res.status_code == 409
    assert "detail" in res.json()


async def test_update_episode_not_found(ac):
    res = await ac.patch(
        f"/v1/episodes/{uuid7str()}",
        json={
            "title": "Valid Title",
            "episode_number": 1,
            "duration": 77,
        },
    )
    assert res.status_code == 404
    assert "detail" in res.json()


async def test_delete_episode(ac, get_all_episodes):
    for episode in islice(get_all_episodes, 2):
        assert (await ac.get(f"/v1/episodes/{episode['id']}")).status_code == 200
        assert (await ac.delete(f"/v1/episodes/{episode['id']}")).status_code == 204
        assert (await ac.get(f"/v1/episodes/{episode['id']}")).status_code == 404
