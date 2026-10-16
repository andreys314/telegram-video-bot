import pytest

from bot.use_cases import format_duration, get_available_resolutions


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (0, "00:00"),
        (45, "00:45"),
        (65, "01:05"),
        (3599, "59:59"),
        (3600, "01:00:00"),
        (8796.0, "02:26:36"),
        (8900, "02:28:20"),
    ],
)
def test_format_duration(seconds: float, expected: str):
    assert expected == format_duration(seconds)


@pytest.mark.parametrize(
    "formats, expected",
    [
        (
            [
                {"height": 1080, "vcodec": "avc1"},
                {"height": 720, "vcodec": "vp9"},
                {"height": 1080, "vcodec": "av01"},
            ],
            [720, 1080],
        ),
        (
            [
                {"height": None, "vcodec": "none"},
                {"height": 90, "vcodec": "none"},
                {"height": 720, "vcodec": "avc1"},
            ],
            [720],
        ),
        (
            [],
            [],
        ),
    ],
)
def test_get_available_resolutions(formats: list[dict], expected: list[int]):
    assert expected == get_available_resolutions(formats)
