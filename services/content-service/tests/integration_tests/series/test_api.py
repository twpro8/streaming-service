import pytest


series_ids = []


@pytest.mark.order(2)
@pytest.mark.parametrize(
    "params, expected_count",
    [
        ({"page": 1, "per_page": 30}, 5),
        ({"page": 1, "per_page": 2}, 2),
        ({"page": 2, "per_page": 2}, 2),
        ({"page": 3, "per_page": 2}, 1),
        # Exact title match
        ({"title": "Bad"}, 1),
        ({"title": "Things"}, 1),
        # Director filter
        ({"director": "Johan Renck"}, 1),
        ({"director": "The Duffer"}, 1),
        ({"director": "Guy"}, 0),
        # Description filter
        ({"description": "the"}, 4),
        ({"description": "diagnosed with cancer"}, 1),
        ({"description": "story of the chernobyl"}, 1),
        # Exact release_year
        ({"release_year": "2000-01-01"}, 1),
        ({"release_year": "2003-01-01"}, 1),
        ({"release_year": "2004-01-01"}, 1),
        # release_year_ge
        ({"release_year_ge": "1899-01-01"}, 5),
        # release_year_le
        ({"release_year_le": "2005-01-01"}, 5),
        # release_year range
        (
            {
                "release_year_ge": "2002-01-01",
                "release_year_le": "2004-01-01",
            },
            3,
        ),
        # Rating
        ({"rating": "0.0"}, 5),
        ({"rating_ge": "1.0"}, 0),
        ({"rating_le": "5"}, 5),
        # No match
        ({"title": "NotExists"}, 0),
        ({"title": "The Hidden Sparrow"}, 0),
        ({"description": "About life exp"}, 0),
        ({"director": "Some guy"}, 0),
        ({"release_year": "1999-01-01"}, 0),
        ({"release_year_ge": "2005-01-01"}, 0),
        ({"release_year_le": "1999-01-01"}, 0),
        # AND CASES FOR GENRES
    ],
)
async def test_get_series(ac, params, expected_count):
    res = await ac.get("/series", params=params)
    data = res.json()["data"]

    assert res.status_code == 200
    assert isinstance(data, list)
    assert len(data) == expected_count


@pytest.mark.parametrize(
    "title, description, director, release_year, cover_url, status_code",
    [
        # Valid data
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "2005-01-01",
            "https://example.com/valid_url.jpg",
            201,
        ),
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "1999-09-09",
            None,
            201,
        ),
        # Invalid title
        ("", "Valid Description", "Valid Director", "2006-01-01", None, 422),
        ("T" * 256, "Valid Description", "Valid Director", "2006-01-01", None, 422),
        # Invalid description
        ("Valid Title", "", "Valid Director", "2020-01-01", None, 422),
        ("Valid Title", "D" * 256, "Valid Director", "2020-01-01", None, 422),
        # Invalid director
        ("Valid Title", "Valid Description", "", "2020-01-01", None, 422),
        ("Valid Title", "Valid Description", "D" * 50, "2020-01-01", None, 422),
        # Invalid release year
        ("Valid Title", "Valid Description", "Valid Director", "10-01-01", None, 422),
        ("Valid Title", "Valid Description", "Valid Director", "some-garbage-here", None, 422),
        ("Valid Title", "Valid Description", "Valid Director", 1, None, 422),
        ("Valid Title", "Description", "Director", "2100-01-01", None, 422),
        ("Valid Title", "Description", "Director", "999-01-01", None, 422),
        # Invalid cover url
        ("Valid Title", "Valid Description", "Valid Director", "2020-01-01", "not-a-url", 422),
        ("Valid Title", "Valid Description", "Valid Director", "2020-01-01", 1, 422),
        # All optional fields None (cover_url) - should succeed
        ("Valid Title", "Valid Description", "Valid Director", "2020-01-01", None, 201),
        # Conflict
        (
            "Valid Title",
            "Valid Description",
            "Valid Director",
            "2020-01-01",
            "https://example.com/valid_url.jpg",
            409,
        ),
    ],
)
async def test_add_series(
    ac,
    title,
    description,
    director,
    release_year,
    cover_url,
    status_code,
):
    request_json = {
        "title": title,
        "description": description,
        "director": director,
        "release_year": release_year,
        "cover_url": cover_url,
    }
    res = await ac.post("/series", json=request_json)
    assert res.status_code == status_code

    if status_code == 201:
        added_series = res.json()["data"]

        assert added_series["title"] == title
        assert added_series["description"] == description
        assert added_series["director"] == director
        assert added_series["release_year"] == release_year
        assert added_series["cover_url"] == cover_url

        series_ids.append(added_series["id"])


@pytest.mark.parametrize(
    "update_data, status_code, series_id",
    [
        # Update title
        ({"title": "Title Updated"}, 200, "bf7264e9-6e93-424a-a1f5-943b55f1e102"),
        ({"title": "Title Updated"}, 200, None),
        # Invalid title
        ({"title": ""}, 422, None),
        ({"title": "T" * 256}, 422, None),
        # Update description
        ({"description": "Description Updated"}, 200, "bf7264e9-6e93-424a-a1f5-943b55f1e102"),
        ({"description": "Description Updated"}, 200, None),
        # Invalid description
        ({"description": ""}, 422, None),
        ({"description": "D" * 256}, 422, None),
        # Update director
        ({"director": "Director Updated"}, 200, "bf7264e9-6e93-424a-a1f5-943b55f1e102"),
        ({"director": "Director Updated"}, 200, None),
        # Invalid director
        ({"director": ""}, 422, None),
        ({"director": "D" * 50}, 422, None),
        # Update release year
        ({"release_year": "2021-01-01"}, 200, "bf7264e9-6e93-424a-a1f5-943b55f1e102"),
        ({"release_year": "2021-01-01"}, 200, None),
        # Invalid release year
        ({"release_year": "10-01-01"}, 422, None),
        ({"release_year": ""}, 422, None),
        ({"release_year": 1}, 422, None),
        ({"release_year": "2100-01-01"}, 422, None),  # future year
        ({"release_year": "999-01-01"}, 422, None),  # too old
        # Update cover_url
        (
            {"cover_url": "https://example.com/updated.jpg"},
            200,
            "bf7264e9-6e93-424a-a1f5-943b55f1e102",
        ),
        ({"cover_url": "https://example.com/updated.jpg"}, 409, None),  # conflict
        # Invalid cover url
        ({"cover_url": ""}, 422, None),
        ({"cover_url": "invalid-uri"}, 422, None),
        # Update multiple fields
        (
            {"title": "New Title", "description": "New Description", "director": "New Director"},
            200,
            "bf7264e9-6e93-424a-a1f5-943b55f1e102",
        ),
        (
            {"title": "New Title", "description": "New Description", "director": "New Director"},
            200,
            None,
        ),
        (
            {
                "release_year": "2022-01-01",
                "cover_url": "https://example.com/test.jpg",
            },
            200,
            "bf7264e9-6e93-424a-a1f5-943b55f1e102",
        ),
        (
            {
                "release_year": "2022-01-01",
                "cover_url": "https://example.com/test.jpg",
            },
            409,
            None,
        ),  # conflict
    ],
)
async def test_update_series(
    ac,
    update_data,
    status_code,
    series_id,
):
    series_id = series_id or series_ids[0]
    res = await ac.patch(f"/series/{series_id}", json=update_data)
    assert res.status_code == status_code


async def test_delete_series(ac):
    for series_id in series_ids:
        assert (await ac.get(f"/series/{series_id}")).status_code == 200
        assert (await ac.delete(f"/series/{series_id}")).status_code == 204
        assert (await ac.get(f"/series/{series_id}")).status_code == 404
