# mcp-weather

An MCP server for current conditions and forecasts from the US [National Weather Service](https://www.weather.gov/documentation/services-web-api) at a fixed home location.

## Setup

Copy `.env.example` to `.env` and set your latitude, longitude, and contact details, which the National Weather Service asks clients to send.

## Run

Requires [uv](https://docs.astral.sh/uv/) and [Task](https://taskfile.dev/).

```sh
task setup
task serve
```

The server listens at `http://localhost:8000/mcp`.

## Docker

```sh
docker compose up -d
```

## Tools

All tools use the configured location and return US units.

- `current_conditions()`: the latest observation: temperature, feels-like, humidity, wind, pressure, visibility, recent precipitation, and a short description.
- `forecast(days=3)`: half-day forecast periods for the next 1 to 7 days with temperature, chance of precipitation, wind, and a detailed description.
- `hourly_forecast(hours=12)`: hour-by-hour forecast for the next 1 to 48 hours.

## Development

```sh
task check    # tests, lint, formatting
```

## License

[MIT](LICENSE)
