"""Module for connecting to Judo Connectivity Module via REST API.

This module provides a client for interacting with the Judo water treatment system's
REST API, allowing for monitoring and control of the device.
"""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfVolume
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import JudoCoordinator
from .judo import JudoAPI

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Judo Connectivity Module sensors based on a config entry."""
    api: JudoAPI = hass.data[DOMAIN][config_entry.entry_id]

    coordinator = JudoCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    entities = [
        JudoSensor(
            coordinator,
            config_entry,
            "soft_water_volume",
            "Soft Water Volume",
            UnitOfVolume.CUBIC_METERS,
            SensorDeviceClass.WATER,
            SensorStateClass.TOTAL_INCREASING,
        ),
        # Add additional entities here if needed
    ]

    async_add_entities(entities)


def device_info(coordinator) -> dict:
    """Return device info for the Judo Connectivity Module."""
    return {
        "identifiers": {(DOMAIN, coordinator.data.get("device_id"))},
        "name": "JUDO Connectivity Module",
        "manufacturer": "JUDO",
        "model": "Connectivity Module",
        # Add other device attributes if available
    }


class JudoSensor(CoordinatorEntity, SensorEntity):
    """Representation of a generic Judo sensor."""

    def __init__(
        self,
        coordinator: JudoCoordinator,
        config_entry: ConfigEntry,
        key: str,
        name: str,
        unit: str,
        device_class: str,
        state_class: str | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{config_entry.entry_id}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_device_info = device_info(coordinator)

    @property
    def state(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._key)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
