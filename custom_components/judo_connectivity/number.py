"""Number entities for Judo Connectivity."""

import logging

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import JudoCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number entity for Judo Connectivity."""
    coordinator: JudoCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        [
            JudoNumber(
                coordinator,
                config_entry,
                NumberEntityDescription(
                    key="salt_refill",
                    native_min_value=0.0,
                    native_max_value=25.0,
                    native_step=0.1,
                    native_unit_of_measurement="kg",
                ),
            )
        ]
    )


class JudoNumber(NumberEntity):
    """Representation of a Judo Connectivity number entity."""

    def __init__(
        self,
        coordinator: JudoCoordinator,
        config_entry: ConfigEntry,
        description: NumberEntityDescription,
    ) -> None:
        """Initialize the number entity."""
        self.entity_description = description
        self._attr_name = "Salt Refill"
        self._attr_unique_id = f"{config_entry.entry_id}_salt_refill"
        self._coordinator = coordinator
        self._attr_native_value = 0.0  # Default value

    async def async_set_native_value(self, value: float) -> None:
        """Set the number value."""
        self._attr_native_value = value
        _LOGGER.info("Setting salt refill value to %.1f kg", value)
        # Integrate API call to set the value in the device, if necessary.
        self.async_write_ha_state()
