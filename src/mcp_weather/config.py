"""Server configuration from environment variables."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    latitude: float
    longitude: float
    contact: str
    location_name: str = "home"
    station: str | None = None


def from_env() -> Config:
    """Build a Config from WEATHER_* variables, exiting with a clear message if any is invalid."""
    try:
        latitude = float(os.environ["WEATHER_LATITUDE"])
        longitude = float(os.environ["WEATHER_LONGITUDE"])
    except (KeyError, ValueError):
        raise SystemExit("set WEATHER_LATITUDE and WEATHER_LONGITUDE to decimal degrees in .env")
    contact = os.environ.get("WEATHER_CONTACT", "").strip()
    if not contact:
        raise SystemExit("set WEATHER_CONTACT to an email or URL in .env; the NWS requires it")
    return Config(
        latitude=latitude,
        longitude=longitude,
        contact=contact,
        location_name=os.environ.get("WEATHER_LOCATION_NAME", "").strip() or "home",
        station=os.environ.get("WEATHER_STATION", "").strip() or None,
    )
