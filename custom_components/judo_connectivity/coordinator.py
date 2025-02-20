"""DataUpdateCoordinator for Judo Connectivity Module."""
import logging
from datetime import timedelta

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

class JudoDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Judo data."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: aiohttp.ClientSession,
        host: str,
        port: int,
        username: str,
        password: str,
        update_interval: int,
    ):
        """Initialize."""
        self._session = session
        self._host = host
        self._port = port
        self._auth = aiohttp.BasicAuth(username, password)
        self._base_url = f"http://{host}:{port}/api/rest/"
        super().__init__(
            hass,
            _LOGGER,
            name="Judo Connectivity",
            update_interval=timedelta(seconds=update_interval),
        )
        self._was_unavailable = False

    async def _async_update_data(self):
        """Fetch data from Judo device."""
        commands = ["FF00", "0600", "0100", "2500", "2800", "5600", "5100"]
        data = {}
        try:
            for cmd in commands:
                async with self._session.get(f"{self._base_url}{cmd}", auth=self._auth) as resp:
                    resp.raise_for_status()
                    json_data = await resp.json()
                    data[cmd] = json_data.get("data", "")
            if self._was_unavailable:
                _LOGGER.info("Judo device is back online")
                self._was_unavailable = False
            return data
        except aiohttp.ClientError as err:
            if not self._was_unavailable:
                _LOGGER.warning("Judo device unavailable: %s", err)
                self._was_unavailable = True
            raise UpdateFailed(f"Error communicating with Judo device: {err}") from err
