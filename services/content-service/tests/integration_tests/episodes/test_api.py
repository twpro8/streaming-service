from uuid import uuid4

import pytest

from tests.utils import calculate_expected_length, get_and_validate, count_content


@pytest.mark.parametrize(
    "page, per_page",
    [
        (1, 30),
        (1, 3),
        (2, 3),
        (3, 3),
        (4, 3),
        (5, 3),
        (6, 3),
        (7, 3),
        (8, 3),
    ],
)
async def test_episode_pagination(ac, get_all_episodes, page, per_page):
    expected_count = calculate_expected_length(page, per_page, len(get_all_episodes))
    episodes = await get_and_validate(
        ac, "/v1/episodes", params={"page": page, "per_page": per_page}
    )
    assert len(episodes) == expected_count


@pytest.mark.parametrize(
    "title",
    (
        "Serial 1",
        "Serial 2",
        "Serial 3",
        "Serial 4",
        "Serial 5",
        "Season 1",
        "Season 2",
        "Episode 1",
        "Episode 2",
        "Episode 5",
    ),
)
async def test_get_filter_by_title(ac, get_all_episodes, title, max_pagination):
    episodes = await get_and_validate(ac, "/v1/episodes", params={"title": title, **max_pagination})
    assert len(episodes) == count_content(get_all_episodes, "title", title)


@pytest.mark.parametrize("episode_number", (1, 2, 3))
async def test_get_filter_by_episode_number(ac, get_all_episodes, episode_number, max_pagination):
    episodes = await get_and_validate(
        ac, "/v1/episodes", params={"episode_number": episode_number, **max_pagination}
    )
    expected_count = sum(1 for ep in get_all_episodes if ep["episode_number"] == episode_number)
    assert len(episodes) == expected_count


async def test_get_filter_by_show_id(ac, get_all_shows, max_pagination):
    for show in get_all_shows:
        show_id = str(show["id"])
        episodes = await get_and_validate(
            ac, "/v1/episodes", params={"show_id": show_id, **max_pagination}
        )
        expected_count = sum(1 for ep in episodes if ep["show_id"] == show_id)
        assert len(episodes) == expected_count


async def test_get_filter_by_season_id(ac, get_all_seasons, max_pagination):
    for season in get_all_seasons:
        season_id = str(season["id"])
        episodes = await get_and_validate(
            ac, "/v1/episodes", params={"season_id": season_id, **max_pagination}
        )
        expected_count = sum(1 for ep in episodes if ep["season_id"] == season_id)
        assert len(episodes) == expected_count


@pytest.mark.parametrize(
    "title, episode_number",
    [
        ("Valid Episode Title 1", 10),
        ("Valid Episode Title 2", 11),
    ],
)
async def test_add_episode_valid(ac, get_all_seasons, title, episode_number):
    for i in range(2):
        show_id = str(get_all_seasons[i]["show_id"])
        season_id = str(get_all_seasons[i]["id"])

        res = await ac.post(
            "/v1/episodes",
            json={
                "show_id": show_id,
                "season_id": season_id,
                "title": title,
                "episode_number": episode_number,
                "duration": 77,
            },
        )
        assert res.status_code == 201
        episode_id = res.json()["data"]["id"]
        season = await get_and_validate(ac, f"/v1/episodes/{episode_id}", expect_list=False)
        assert season["title"] == title
        assert season["episode_number"] == episode_number


async def test_add_valid_episode_with_video_url(ac, get_all_seasons):
    show_id = str(get_all_seasons[0]["show_id"])
    season_id = str(get_all_seasons[0]["id"])
    video_url = "https://www.example.com/video.avi"
    res = await ac.post(
        "/v1/episodes",
        json={
            "show_id": show_id,
            "season_id": season_id,
            "title": "Valid Title",
            "episode_number": 13,
            "duration": 77,
            "video_url": video_url,
        },
    )
    assert res.status_code == 201
    episode_id = res.json()["data"]["id"]
    season = await get_and_validate(ac, f"/v1/episodes/{episode_id}", expect_list=False)
    assert season["video_url"] == video_url


@pytest.mark.parametrize(
    "field, value",
    [
        ("title", "t"),
        ("title", "t" * 256),
        ("episode_number", 0),
        ("episode_number", 10000),
        ("duration", 0),
        ("duration", 513),
        ("video_url", "invalid-format"),
        ("extra", "Hello, World!"),
    ],
)
async def test_add_episode_invalid(ac, get_all_seasons, field, value):
    show_id = str(get_all_seasons[0]["show_id"])
    season_id = str(get_all_seasons[0]["id"])

    res = await ac.post(
        "/v1/episodes",
        json={
            "show_id": show_id,
            "season_id": season_id,
            "title": "Valid Episode Title 3",
            "episode_number": 14,
            "duration": 77,
            "video_url": "https://www.example.com/videos/main.mp4",
            field: value,
        },
    )
    assert res.status_code == 422


@pytest.mark.parametrize(
    "episode_number, video_url",
    (
        (17, None),
        (None, "https://www.video.com/movie.mp4"),
    ),
)
async def test_add_episode_on_conflict(ac, get_all_seasons, episode_number, video_url):
    show_id = str(get_all_seasons[0]["show_id"])
    season_id = str(get_all_seasons[0]["id"])
    ep_num = episode_number or 15

    req_body = {
        "show_id": show_id,
        "season_id": season_id,
        "title": "Valid Title",
        "episode_number": ep_num,
        "duration": 77,
        "video_url": None,
    }

    res = await ac.post("/v1/episodes", json=req_body)
    assert res.status_code == 201

    if not episode_number:
        ep_num += 1

    res = await ac.post("/v1/episodes", json={"episode_number": ep_num, **req_body})
    assert res.status_code == 409


@pytest.mark.parametrize(
    "show_id, season_id",
    [
        (str(uuid4()), None),
        (None, str(uuid4())),
    ],
)
async def test_add_episode_not_found(ac, get_all_episodes, show_id, season_id):
    show_id_val = show_id or str(get_all_episodes[0]["show_id"])
    season_id_val = season_id or str(get_all_episodes[0]["season_id"])

    res = await ac.post(
        "/v1/episodes",
        json={
            "show_id": show_id_val,
            "season_id": season_id_val,
            "title": "Valid Title",
            "episode_number": 16,
            "duration": 77,
        },
    )
    assert res.status_code == 404
    detail = res.json()["detail"]

    if show_id:
        assert "show" in detail.strip().lower()
    else:
        assert "season" in detail.strip().lower()


@pytest.mark.parametrize(
    "field, value",
    [
        ("title", "Title Updated"),
        ("episode_number", 20),
        ("duration", 80),
        ("video_url", "https://www.updated.com/updated.avi"),
        ("video_url", None),
    ],
)
async def test_update_episode_valid(ac, get_all_episodes, field, value):
    episode_id = str(get_all_episodes[0]["id"])
    res = await ac.patch(f"/v1/episodes/{episode_id}", json={field: value})
    assert res.status_code == 200

    episode = await get_and_validate(ac, f"/v1/episodes/{episode_id}", expect_list=False)
    assert episode[field] == value


@pytest.mark.parametrize(
    "field, value",
    [
        ("title", "t"),
        ("title", "t" * 256),
        ("episode_number", 0),
        ("episode_number", 10000),
        ("duration", 0),
        ("duration", 513),
        ("video_url", "invalid-format"),
    ],
)
async def test_update_episode_invalid(ac, get_all_episodes, field, value):
    episode_id = str(get_all_episodes[0]["id"])
    res = await ac.patch(f"/v1/episodes/{episode_id}", json={field: value})
    assert res.status_code == 422


@pytest.mark.parametrize(
    "field, value",
    [
        ("episode_number", 21),
        ("video_url", "https://www.test120.com/test120.avi"),
    ],
)
async def test_update_episode_on_conflict(ac, get_all_seasons, field, value):
    season_id = str(get_all_seasons[0]["id"])
    episodes = await get_and_validate(ac, "/v1/episodes", params={"season_id": season_id})
    assert len(episodes) >= 2

    res = await ac.patch(f"/v1/episodes/{episodes[0]['id']}", json={field: value})
    assert res.status_code == 200

    res = await ac.patch(f"/v1/episodes/{episodes[1]['id']}", json={field: value})
    assert res.status_code == 409


async def test_update_episode_not_found(ac):
    res = await ac.patch(
        f"/v1/episodes/{str(uuid4())}",
        json={
            "title": "Valid Title",
            "episode_number": 22,
            "duration": 77,
        },
    )
    assert res.status_code == 404

    detail = res.json()["detail"]
    assert "episode" in detail.strip().lower()


async def test_delete_episode(ac, get_all_episodes):
    for episode in get_all_episodes[:5]:
        assert (await ac.get(f"/v1/episodes/{episode['id']}")).status_code == 200
        assert (await ac.delete(f"/v1/episodes/{episode['id']}")).status_code == 204
        assert (await ac.get(f"/v1/episodes/{episode['id']}")).status_code == 404
