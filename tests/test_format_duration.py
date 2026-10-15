import pytest

from bot.use_cases import format_duration


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (0, '00:00'),
        (45, '00:45'),
        (65, "01:05"),
        (3599, "59:59"),
        (3600, "01:00:00"),
        (8796.0, "02:26:36"),
        (8900, '02:28:20'),
    ]
)
def test_format_duration(seconds: int | float, expected: str):
    assert expected == format_duration(seconds)
