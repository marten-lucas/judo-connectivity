"""Button entities for Judo Connectivity."""

import logging

from homeassistant.components.button import ButtonEntity
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
    """Set up the button entity for Judo Connectivity."""
    coordinator: JudoCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        [
            JudoButton(
                coordinator,
                config_entry,
                name="Refill Salt",
            )
        ]
    )


class JudoButton(ButtonEntity):
    """Representation of a Judo Connectivity button entity."""

    def __init__(
        self, coordinator: JudoCoordinator, config_entry: ConfigEntry, name: str
    ) -> None:
        """Initialize the button entity."""
        self._coordinator = coordinator
        self._attr_name = name
        self._attr_unique_id = f"{config_entry.entry_id}_refill_salt"

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.info("Button '%s' pressed", self._attr_name)
        # Add API call here if needed in the future
