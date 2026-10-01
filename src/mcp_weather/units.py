"""Conversions from the metric values pynws returns to US customary units."""

COMPASS = [
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
]  # fmt: skip


def rounded(value: float | None, digits: int) -> float | int | None:
    if value is None:
        return None
    return round(value) if digits == 0 else round(value, digits)


def c_to_f(celsius: float | None, digits: int = 0) -> float | int | None:
    return None if celsius is None else rounded(celsius * 9 / 5 + 32, digits)


def kmh_to_mph(kmh: float | None, digits: int = 0) -> float | int | None:
    return None if kmh is None else rounded(kmh / 1.609344, digits)


def pa_to_inhg(pascals: float | None, digits: int = 2) -> float | int | None:
    return None if pascals is None else rounded(pascals / 3386.389, digits)


def m_to_mi(meters: float | None, digits: int = 1) -> float | int | None:
    return None if meters is None else rounded(meters / 1609.344, digits)


def mm_to_in(millimeters: float | None, digits: int = 2) -> float | int | None:
    return None if millimeters is None else rounded(millimeters / 25.4, digits)


def degrees_to_compass(degrees: float | None) -> str | None:
    if degrees is None:
        return None
    return COMPASS[round(degrees / 22.5) % 16]
