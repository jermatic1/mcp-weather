import anyio
import pytest
from mcp.server.mcpserver.exceptions import ToolError
from pynws import NwsError

from mcp_weather.config import Config
from mcp_weather.nws import WeatherClient


class FakeNws:
    def __init__(self, fail=False):
        self.calls = 0
        self.fail = fail
        self.observation = {"temperature": 1.0}

    async def update_observation(self, **_):
        self.calls += 1
        if self.fail:
            raise NwsError("boom")


def make_client(fake):
    client = WeatherClient(Config(1.0, 2.0, "test@example.com"))

    async def nws():
        return fake

    client._nws = nws
    return client


def test_observation_is_cached():
    fake = FakeNws()
    client = make_client(fake)

    async def run():
        return await client.observation(), await client.observation()

    first, second = anyio.run(run)
    assert first == second == {"temperature": 1.0}
    assert fake.calls == 1


def test_nws_error_becomes_tool_error():
    client = make_client(FakeNws(fail=True))
    with pytest.raises(ToolError, match="National Weather Service request failed"):
        anyio.run(client.observation)
