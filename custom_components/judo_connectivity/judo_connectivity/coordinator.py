"""Data update coordinator for Judo Connectivity Module."""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .judo import JudoClient

_LOGGER = logging.getLogger(__name__)


class JudoDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Judo data."""

    def __init__(
        self, hass: HomeAssistant, client: JudoClient, update_interval: int
    ) -> None:
        """Initialize the coordinator."""
        self.client = client
        super().__init__(
            hass,
            _LOGGER,
            name="Judo Connectivity Module",
            update_interval=timedelta(seconds=update_interval),
        )

    async def _async_update_data(self) -> dict[str, any]:
        """Fetch data from Judo device."""
        try:
            data = {}
            data["device_type"] = await self.client.async_fetch_data("FF00")
            data["device_no"] = await self.client.async_fetch_data("0600")
            data["sw_version"] = await self.client.async_fetch_data("0100")
            data["operating_hours"] = await self.client.async_fetch_data("2500")
            data["total_water_volume"] = await self.client.async_fetch_data("2900")  # Updated to 2900
            salt_data = await self.client.async_fetch_data("5600")
            data["salt_range"] = salt_data
            data["salt_stock"] = salt_data
            data["water_hardness"] = await self.client.async_fetch_data("5100")
            return data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with Judo device: {err}") from err
        else:
            return data
