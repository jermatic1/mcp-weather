import pytest

from mcp_weather import units


@pytest.mark.parametrize(
    "func, value, expected",
    [
        (units.c_to_f, 20, 68),
        (units.c_to_f, -40, -40),
        (units.kmh_to_mph, 16.09344, 10),
        (units.pa_to_inhg, 101325, 29.92),
        (units.m_to_mi, 16093.44, 10.0),
        (units.mm_to_in, 25.4, 1.0),
        (units.degrees_to_compass, 0, "N"),
        (units.degrees_to_compass, 270, "W"),
        (units.degrees_to_compass, 359, "N"),
    ],
)
def test_conversions(func, value, expected):
    assert func(value) == expected


@pytest.mark.parametrize(
    "func",
    [units.c_to_f, units.kmh_to_mph, units.pa_to_inhg, units.m_to_mi, units.mm_to_in,
     units.degrees_to_compass],
)  # fmt: skip
def test_none_passthrough(func):
    assert func(None) is None
