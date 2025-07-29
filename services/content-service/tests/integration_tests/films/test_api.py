from datetime import date
from typing import List
from uuid import UUID

import pytest


films_ids: List[UUID] = []


@pytest.mark.parametrize(
    "title, description, director, release_year, duration, cover_url, status_code",
    [
        # Valid data - should succeed
        (
            "Inception",
            "A mind-bending thriller",
            "Christopher Nolan",
            "2010-07-16",
            148,
            "https://example.com/inception.jpg",
            201,
        ),
        (
            "Rookie",
            "Twisted story",
            "John Nolan",
            "1999-09-09",
            148,
            None,
            201,
        ),
        # Empty title - should fail validation
        ("", "Some description", "Director Name", "2020-01-01", 100, None, 422),
        # Very long title - should fail validation
        ("T" * 300, "Description", "Director", "2020-01-01", 90, None, 422),
        # release_year in the future - should fail validation
        # ("Future Film", "Description", "Director", "2100-01-01", 90, None, 422),
        # Negative duration - should fail validation
        ("Film", "Description", "Director", "2020-01-01", -10, None, 422),
        # Excessively long duration - should fail validation
        ("Long Film", "Description", "Director", "2020-01-01", 10000, None, 422),
        # Invalid cover_url format - should fail validation
        ("Film", "Description", "Director", "2020-01-01", 90, "not-a-url", 422),
        # Empty director - should fail validation
        ("Film", "Description", "", "2020-01-01", 90, None, 422),
        # All optional fields None (cover_url) - should succeed
        ("Film", "Description", "Director", "2020-01-01", 90, None, 201),
    ],
)
async def test_add_film(
    ac,
    title: str,
    description: str,
    director: str,
    release_year: date,
    duration: int,
    cover_url: str,
    status_code: int,
):
    request_json = {
        "title": title,
        "description": description,
        "director": director,
        "release_year": release_year,
        "duration": duration,
        "cover_url": cover_url,
    }

    res = await ac.post("/films", json=request_json)
    assert res.status_code == status_code

    if status_code == 201:
        added_film = res.json()["data"]

        assert added_film["title"] == title
        assert added_film["description"] == description
        assert added_film["director"] == director
        assert added_film["release_year"] == release_year
        assert added_film["duration"] == duration
        assert added_film["cover_url"] == cover_url

        global films_ids
        films_ids.append(added_film["id"])


@pytest.mark.parametrize(
    "params, expected_count",
    [
        # No filters — should return all 8
        ({"page": 1, "per_page": 30}, 8),
        # Exact title match
        ({"title": "Inception", "page": 1, "per_page": 30}, 1),
        ({"title": "The Hidden Forest", "page": 1, "per_page": 30}, 1),
        # Director filter
        ({"director": "Christopher Nolan", "page": 1, "per_page": 30}, 1),
        ({"director": "Clara Syntax", "page": 1, "per_page": 30}, 1),
        ({"director": "Nonexistent", "page": 1, "per_page": 30}, 0),
        # Description filter
        ({"description": "thriller", "page": 1, "per_page": 30}, 1),  # Only "Inception"
        ({"description": "lost tribe", "page": 1, "per_page": 30}, 1),  # Only "The Hidden Forest"
        # Exact release_year
        ({"release_year": "2025-02-14", "page": 1, "per_page": 30}, 1),  # "Love in Beta"
        ({"release_year": "1999-09-09", "page": 1, "per_page": 30}, 1),  # "Rookie"
        ({"release_year": "2018-06-10", "page": 1, "per_page": 30}, 1),  # "The Hidden Forest"
        # release_year_ge
        (
            {"release_year_ge": "2025-01-01", "page": 1, "per_page": 30},
            2,
        ),  # "Love in Beta" + "Desert Frequency"
        # release_year_le
        ({"release_year_le": "2000-01-01", "page": 1, "per_page": 30}, 1),  # "Rookie"
        # release_year range
        (
            {
                "release_year_ge": "2020-01-01",
                "release_year_le": "2025-12-31",
                "page": 1,
                "per_page": 30,
            },
            4,
        ),
        # No match
        ({"title": "NotExists", "page": 1, "per_page": 30}, 0),
    ],
)
async def test_get_films(ac, params, expected_count):
    res = await ac.get("/films", params=params)
    data = res.json()["data"]

    assert res.status_code == 200
    assert isinstance(data, list)
    assert len(data) == expected_count


async def test_get_one_film(ac, get_films_ids):
    for film_id in films_ids + get_films_ids:
        res = await ac.get(f"/films/{film_id}")
        data = res.json()["data"]

        assert res.status_code == 200
        assert isinstance(data, dict)
        assert data["id"] == film_id


@pytest.mark.parametrize(
    "title, description, director, release_year, duration, cover_url, video_url, status_code",
    [
        # Valid full update - all fields set correctly
        (
            "Interstellar",
            "Space exploration epic",
            "Christopher Nolan",
            "2014-11-07",
            169,
            "https://example.com/interstellar.jpg",
            "https://cdn.example.com/video1.mp4",
            200,
        ),
        # Empty title - invalid
        ("", "No title", "Director", "2020-01-01", 100, None, None, 422),
        # Too long title - invalid
        ("X" * 256, "Long title", "Director", "2020-01-01", 90, None, None, 422),
        # Future release year - invalid
        # ("Future Movie", "Desc", "Director", "2100-01-01", 100, None, None, 422),
        # Negative duration - invalid
        ("Bad Duration", "Desc", "Director", "2020-01-01", -50, None, None, 422),
        # Excessive duration - invalid
        ("Too Long", "Desc", "Director", "2020-01-01", 10000, None, None, 422),
        # Invalid cover_url format - invalid
        ("Invalid URL", "Desc", "Director", "2020-01-01", 90, "not-a-url", None, 422),
        # Valid update with null cover and video
        ("Minimal", "Just enough", "Someone", "2015-03-03", 88, None, None, 200),
        # Empty director - invalid
        ("Nameless", "Good movie", "", "2020-01-01", 90, None, None, 422),
        # Invalid video_url format - invalid
        ("Bad Video URL", "Test", "Test Director", "2020-01-01", 90, None, "not-a-video-url", 422),
        # Valid video_url provided
        (
            "Video Ready",
            "Has video link",
            "Test Director",
            "2021-06-06",
            100,
            "https://example.com/cover.jpg",
            "https://cdn.example.com/video.mp4",
            200,
        ),
        # cover_url and video_url both null - valid
        ("No Media", "Just text.", "Director", "2010-10-10", 95, None, None, 200),
        # cover_url valid, video_url null - valid
        (
            "Cover Only",
            "Visuals only",
            "Director",
            "2018-08-08",
            110,
            "https://example.com/cover2.jpg",
            None,
            200,
        ),
        # cover_url null, video_url valid - valid
        (
            "Streamable",
            "Only online",
            "Director",
            "2019-09-09",
            105,
            None,
            "https://cdn.example.com/stream.mp4",
            200,
        ),
    ],
)
async def test_replace_film(
    ac,
    title: str,
    description: str,
    director: str,
    release_year: str,
    duration: int,
    cover_url: str,
    video_url: str,
    status_code: int,
):
    request_json = {
        "title": title,
        "description": description,
        "director": director,
        "release_year": release_year,
        "duration": duration,
        "cover_url": cover_url,
        "video_url": video_url,
    }
    film_id = films_ids[-1]
    res = await ac.put(f"/films/{film_id}", json=request_json)
    assert res.status_code == status_code


@pytest.mark.parametrize(
    "update_data, status_code",
    [
        # Update title only
        ({"title": "Updated Title"}, 200),
        # Update description only
        ({"description": "New description of the film."}, 200),
        # Update director only
        ({"director": "Updated Director"}, 200),
        # Update release_year only
        ({"release_year": "2021-01-01"}, 200),
        # Update duration only
        ({"duration": 120}, 200),
        # Update cover_url only
        ({"cover_url": "https://example.com/updated.jpg"}, 200),
        # Update video_url only
        ({"video_url": "https://cdn.example.com/newvideo.mp4"}, 200),
        # Update multiple fields
        ({"title": "New Title", "description": "New Description", "duration": 99}, 200),
        # Invalid duration (negative)
        ({"duration": -10}, 422),
        # Invalid release_year (future date)
        # ({"release_year": "2100-01-01"}, 422),
        # Invalid cover_url
        ({"cover_url": "not-a-valid-url"}, 422),
        # Invalid video_url
        ({"video_url": "bad-url"}, 422),
        # Empty title — should fail if not allowed
        ({"title": ""}, 422),
        # Empty director — should fail
        ({"director": ""}, 422),
    ],
)
async def test_update_film(
    ac,
    update_data: dict,
    status_code: int,
):
    film_id = films_ids[0]
    res = await ac.patch(f"/films/{film_id}", json=update_data)
    assert res.status_code == status_code


async def test_delete_film(ac):
    global films_ids

    for film_id in films_ids[:]:
        res = await ac.delete(f"/films/{film_id}")
        assert res.status_code == 204

        res = await ac.get(f"/films/{film_id}")
        assert res.status_code == 404

        films_ids.remove(film_id)

    assert len(films_ids) == 0
