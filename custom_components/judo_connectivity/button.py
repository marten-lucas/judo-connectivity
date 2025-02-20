"""Button entity for Judo Connectivity Module."""

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import JudoDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the button platform."""
    coordinator: JudoDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([JudoSaltRefillTriggerButton(coordinator, entry)])


class JudoSaltRefillTriggerButton(ButtonEntity):
    """Representation of the Regeneration Salt Refill Trigger button."""

    _attr_name = "Regeneration Salt Trigger Refill"
    _attr_icon = "mdi:refresh"

    def __init__(
        self, coordinator: JudoDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the button."""
        self.coordinator = coordinator
        self._entry = entry
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{entry.unique_id}_salt_refill_trigger"

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.unique_id)},
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    async def async_press(self) -> None:
        """Handle the button press."""
        # Get the refill mass from the number entity
        mass_kg = self.hass.states.get(
            f"number.{self._entry.unique_id}_regeneration_salt_refill_mass"
        )
        if mass_kg is None:
            raise HomeAssistantError("Refill mass not set")
        mass_grams = int(float(mass_kg.state) * 1000)
        await self.coordinator.client.async_set_salt_refill(mass_grams)
        await self.coordinator.async_request_refresh()
