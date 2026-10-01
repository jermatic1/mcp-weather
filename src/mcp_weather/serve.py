"""MCP server exposing National Weather Service data for the configured home location."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

from mcp_weather import units
from mcp_weather.config import Config
from mcp_weather.nws import WeatherClient

READ_ONLY = ToolAnnotations(readOnlyHint=True, openWorldHint=True)


def create(client: WeatherClient, location_name: str) -> MCPServer:
    @asynccontextmanager
    async def lifespan(_: MCPServer) -> AsyncIterator[None]:
        try:
            yield
        finally:
            await client.close()

    server = MCPServer(
        "weather",
        instructions=(
            f"Current conditions and forecasts from the US National Weather Service for "
            f"{location_name} only. All tools use this fixed location and return US units "
            "(°F, mph, inHg, miles, inches)."
        ),
        lifespan=lifespan,
    )

    @server.tool(annotations=READ_ONLY)
    async def current_conditions() -> dict[str, Any]:
        """Latest observed weather: temperature, feels-like, humidity, wind, pressure,
        visibility, recent precipitation, and a short description. Fields the station did
        not report are omitted.
        """
        return _shape_observation(await client.observation(), location_name)

    @server.tool(annotations=READ_ONLY)
    async def forecast(days: int = 3) -> list[dict]:
        """Forecast in half-day periods (e.g. "Today", "Tonight") for the next 1 to 7 days,
        each with temperature, chance of precipitation, wind, and a detailed description.
        """
        periods = await client.forecast()
        return [_shape_period(p) for p in periods[: max(1, min(days, 7)) * 2]]

    @server.tool(annotations=READ_ONLY)
    async def hourly_forecast(hours: int = 12) -> list[dict]:
        """Hour-by-hour forecast for the next 1 to 48 hours with temperature, chance of
        precipitation, humidity, wind, and a short description.
        """
        periods = await client.forecast_hourly()
        return [_shape_hour(p) for p in periods[: max(1, min(hours, 48))]]

    return server


def _shape_observation(obs: dict, location_name: str) -> dict:
    observed = datetime.fromisoformat(obs["timestamp"]) if obs.get("timestamp") else None
    feels_like = _first(obs.get("windChill"), obs.get("heatIndex"), obs.get("temperature"))
    pressure = _first(obs.get("seaLevelPressure"), obs.get("barometricPressure"))
    speed = units.kmh_to_mph(obs.get("windSpeed"))
    direction = obs.get("windDirection") if speed else None
    wind = _compact(
        {
            "speed_mph": speed,
            "gust_mph": units.kmh_to_mph(obs.get("windGust")),
            "direction": units.degrees_to_compass(direction),
            "direction_deg": direction,
        }
    )
    station = obs.get("station")
    shaped = _compact(
        {
            "location": location_name,
            "station": station and station.rsplit("/", 1)[-1],
            "observed_at": observed and observed.astimezone().isoformat(timespec="minutes"),
            "age_minutes": observed and round((datetime.now(UTC) - observed).total_seconds() / 60),
            "description": obs.get("textDescription"),
            "temperature_f": units.c_to_f(obs.get("temperature")),
            "feels_like_f": units.c_to_f(feels_like),
            "dewpoint_f": units.c_to_f(obs.get("dewpoint")),
            "humidity_pct": units.rounded(obs.get("relativeHumidity"), 0),
            "wind": wind or None,
            "pressure_inhg": units.pa_to_inhg(pressure),
            "visibility_mi": units.m_to_mi(obs.get("visibility")),
            "precipitation_last_hour_in": units.mm_to_in(obs.get("precipitationLastHour")),
            "high_last_24h_f": units.c_to_f(obs.get("maxTemperatureLast24Hours")),
            "low_last_24h_f": units.c_to_f(obs.get("minTemperatureLast24Hours")),
            "icon": obs.get("icon"),
        }
    )
    shaped.setdefault("temperature_f", None)
    shaped.setdefault("description", None)
    return shaped


def _shape_period(period: dict) -> dict:
    return _compact(
        {
            "name": period.get("name"),
            "start": period.get("startTime"),
            "end": period.get("endTime"),
            "is_daytime": period.get("isDaytime"),
            "temperature_f": period.get("temperature"),
            "precip_chance_pct": period.get("probabilityOfPrecipitation"),
            "wind": " ".join(filter(None, (period.get("windSpeed"), period.get("windDirection")))),
            "short_forecast": period.get("shortForecast"),
            "detailed_forecast": period.get("detailedForecast"),
            "icon": period.get("icon"),
        }
    )


def _shape_hour(period: dict) -> dict:
    return _compact(
        {
            "time": period.get("startTime"),
            "temperature_f": period.get("temperature"),
            "precip_chance_pct": period.get("probabilityOfPrecipitation"),
            "humidity_pct": period.get("relativeHumidity"),
            "dewpoint_f": period.get("dewpoint"),
            "wind_mph": period.get("windSpeedAvg"),
            "wind_direction": period.get("windDirection"),
            "short_forecast": period.get("shortForecast"),
        }
    )


def _first(*values):
    return next((v for v in values if v is not None), None)


def _compact(data: dict) -> dict:
    return {k: v for k, v in data.items() if v not in (None, "")}


def serve(config: Config, host: str, port: int) -> None:
    server = create(WeatherClient(config), config.location_name)
    server.run("streamable-http", host=host, port=port, stateless_http=True)
