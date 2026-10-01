import anyio


def call(server, name, args=None):
    async def run():
        result = await server.call_tool(name, args or {})
        return result.structured_content

    return anyio.run(run)


def test_tool_names(server):
    tools = anyio.run(server.list_tools)
    assert {t.name for t in tools} == {"current_conditions", "forecast", "hourly_forecast"}


def test_current_conditions(server):
    result = call(server, "current_conditions")
    assert result["station"] == "KTEST"
    assert result["temperature_f"] == 68
    assert result["feels_like_f"] == 68
    assert result["humidity_pct"] == 52
    assert result["wind"] == {"speed_mph": 10, "direction": "W", "direction_deg": 270}
    assert result["pressure_inhg"] == 29.92
    assert result["visibility_mi"] == 10.0
    assert result["observed_at"].startswith("2026-10-01T")
    assert "precipitation_last_hour_in" not in result
    assert "high_last_24h_f" not in result


def test_forecast_days(server):
    result = call(server, "forecast", {"days": 1})["result"]
    assert [p["name"] for p in result] == ["Period 0", "Period 1"]
    assert result[0]["wind"] == "7 to 10 mph NW"
    assert result[0]["temperature_f"] == 70


def test_hourly_clamps(server):
    assert len(call(server, "hourly_forecast", {"hours": 100})["result"]) == 20
    result = call(server, "hourly_forecast", {"hours": 2})["result"]
    assert len(result) == 2
    assert result[0]["wind_mph"] == 8.5
