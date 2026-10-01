import pytest

from mcp_weather import serve


class FakeClient:
    """Stands in for WeatherClient, returning pynws-shaped data."""

    def __init__(self, observation, forecast, hourly):
        self.data = {"observation": observation, "forecast": forecast, "forecast_hourly": hourly}

    async def observation(self):
        return self.data["observation"]

    async def forecast(self):
        return self.data["forecast"]

    async def forecast_hourly(self):
        return self.data["forecast_hourly"]

    async def close(self):
        pass


@pytest.fixture
def observation():
    return {
        "temperature": 20.0,
        "dewpoint": 10.0,
        "windChill": None,
        "heatIndex": None,
        "relativeHumidity": 52.4,
        "windSpeed": 16.09344,
        "windGust": None,
        "windDirection": 270,
        "barometricPressure": 100000,
        "seaLevelPressure": 101325,
        "visibility": 16093.44,
        "precipitationLastHour": None,
        "maxTemperatureLast24Hours": None,
        "minTemperatureLast24Hours": None,
        "textDescription": "Mostly Cloudy",
        "icon": "https://api.weather.gov/icons/land/day/bkn?size=medium",
        "station": "https://api.weather.gov/stations/KTEST",
        "timestamp": "2026-10-01T12:00:00+00:00",
    }


def _period(i):
    return {
        "name": f"Period {i}",
        "startTime": f"2026-10-0{1 + i // 2}T{6 if i % 2 == 0 else 18}:00:00-05:00",
        "endTime": f"2026-10-0{1 + i // 2}T{18 if i % 2 == 0 else 23}:00:00-05:00",
        "isDaytime": i % 2 == 0,
        "temperature": 70 + i,
        "temperatureUnit": "F",
        "probabilityOfPrecipitation": 10 * i,
        "windSpeed": "7 to 10 mph",
        "windDirection": "NW",
        "icon": "https://api.weather.gov/icons/land/day/few?size=medium",
        "shortForecast": "Sunny",
        "detailedForecast": "Sunny, with a high near 70.",
    }


def _hour(i):
    return {
        "startTime": f"2026-10-01T{i:02d}:00:00-05:00",
        "temperature": 60 + i,
        "probabilityOfPrecipitation": 0,
        "relativeHumidity": 50,
        "dewpoint": 45,
        "windSpeedAvg": 8.5,
        "windDirection": "N",
        "shortForecast": "Clear",
    }


@pytest.fixture
def server(observation):
    client = FakeClient(observation, [_period(i) for i in range(4)], [_hour(i) for i in range(20)])
    return serve.create(client, "home")
