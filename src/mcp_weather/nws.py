"""Cached access to National Weather Service data for one location via pynws."""

import asyncio
import logging
from time import monotonic
from typing import Any

import aiohttp
from mcp.server.mcpserver.exceptions import ToolError
from pynws import NwsError, SimpleNWS, call_with_retry

from mcp_weather.config import Config

log = logging.getLogger(__name__)

RETRY_INTERVAL = 5
RETRY_STOP = 15
# Only the newest observation; pynws otherwise fills gaps from older, possibly stale, reports.
UPDATE_ARGS = {"observation": {"limit": 1}}


class WeatherClient:
    """Fetches observations and forecasts for the configured location, caching each for a TTL."""

    def __init__(self, config: Config, observation_ttl: int = 600, forecast_ttl: int = 1800):
        self.config = config
        self.ttl = {
            "observation": observation_ttl,
            "forecast": forecast_ttl,
            "forecast_hourly": forecast_ttl,
        }
        self._cache: dict[str, tuple[float, Any]] = {}
        self._lock = asyncio.Lock()
        self._session: aiohttp.ClientSession | None = None
        self._nws_client: SimpleNWS | None = None

    async def observation(self) -> dict:
        data = await self._fetch("observation")
        if not data:
            raise ToolError("no recent observation available from the weather station")
        return data

    async def forecast(self) -> list[dict]:
        return await self._fetch("forecast") or []

    async def forecast_hourly(self) -> list[dict]:
        return await self._fetch("forecast_hourly") or []

    async def close(self) -> None:
        if self._session is not None:
            await self._session.close()

    async def _nws(self) -> SimpleNWS:
        if self._nws_client is None:
            config = self.config
            self._session = aiohttp.ClientSession()
            nws = SimpleNWS(config.latitude, config.longitude, config.contact, self._session)
            await nws.set_station(config.station)
            log.info("using NWS station %s", nws.station)
            self._nws_client = nws
        return self._nws_client

    async def _fetch(self, kind: str) -> Any:
        """Return cached data for `kind`, refreshing it through pynws when older than its TTL."""
        async with self._lock:
            cached = self._cache.get(kind)
            if cached and monotonic() - cached[0] < self.ttl[kind]:
                return cached[1]
            try:
                nws = await self._nws()
                update = getattr(nws, f"update_{kind}")
                await call_with_retry(
                    update, RETRY_INTERVAL, RETRY_STOP, **UPDATE_ARGS.get(kind, {})
                )
            except (TimeoutError, NwsError, aiohttp.ClientError) as exc:
                log.warning("NWS %s request failed: %s", kind, exc)
                raise ToolError(f"National Weather Service request failed: {exc}") from exc
            data = getattr(nws, kind)
            self._cache[kind] = (monotonic(), data)
            return data
