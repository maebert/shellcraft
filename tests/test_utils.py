"""Unit tests for utils helpers."""

from shellcraft.utils import format_duration


def test_seconds_singular():
    assert format_duration(1) == "1 second"


def test_seconds_plural():
    assert format_duration(8) == "8 seconds"


def test_zero():
    assert format_duration(0) == "0 seconds"


def test_negative_clamped_to_zero():
    assert format_duration(-5) == "0 seconds"


def test_floats_are_truncated():
    assert format_duration(8.9) == "8 seconds"


def test_exact_minute_drops_zero_seconds():
    assert format_duration(60) == "1 minute"


def test_minutes_and_seconds():
    assert format_duration(203) == "3 minutes and 23 seconds"


def test_two_minutes_no_seconds():
    assert format_duration(120) == "2 minutes"


def test_one_minute_one_second():
    assert format_duration(61) == "1 minute and 1 second"


def test_exact_hour_drops_zero_minutes():
    assert format_duration(3600) == "1 hour"


def test_hours_and_minutes():
    assert format_duration(3725) == "1 hour and 2 minutes"


def test_multiple_hours():
    assert format_duration(7200) == "2 hours"


def test_hours_drops_residual_seconds():
    """Seconds at the hour scale are noise; format keeps it to hour+minute."""
    assert format_duration(3661) == "1 hour and 1 minute"
