"""Module for connecting to Judo Connectivity Module via REST API.

This module provides a client for interacting with the Judo water treatment system's
REST API, allowing for monitoring and control of the device.
"""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .judo import JudoAPI

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(minutes=1)


class JudoCoordinator(DataUpdateCoordinator):
    """Coordinator to manage data fetching from Judo API."""

    def __init__(self, hass: HomeAssistant, api: JudoAPI) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Judo Connectivity Module Data Coordinator",
            update_interval=UPDATE_INTERVAL,
        )
        self.api = api

    async def _async_update_data(self) -> dict:
        """Fetch data from Judo API."""
        try:
            # Fetch soft water volume
            soft_water_volume = await self.api.get_soft_water_volume()

            # Fetch salt mass and range
            salt_mass, salt_range = await self.api.get_salt()
        except Exception as err:
            _LOGGER.error("Error fetching data from Judo API: %s", err)
            raise UpdateFailed(f"Error fetching data from Judo API: {err}") from err
        else:
            return {
                "soft_water_volume": soft_water_volume,
                "salt_mass": salt_mass,
                "salt_range": salt_range,
            }
