"""Button platform for Judo Connectivity Module."""
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import JudoDataUpdateCoordinator

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Judo button."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    device_info = DeviceInfo(
        identifiers={(DOMAIN, f"{entry.data['host']}:{entry.data['port']}")},
        name=f"Judo Device at {entry.data['host']}",
        manufacturer="Judo",
    )
    async_add_entities([JudoSaltRefillButton(coordinator, device_info)])

class JudoSaltRefillButton(ButtonEntity):
    """Button to trigger salt refill."""

    _attr_name = "Regeneration Salt Trigger Refill"
    _attr_has_entity_name = True
    _attr_translation_key = "salt_refill_trigger"

    def __init__(self, coordinator: JudoDataUpdateCoordinator, device_info: DeviceInfo):
        """Initialize the button."""
        self._coordinator = coordinator
        self._attr_device_info = device_info
        self._attr_unique_id = f"{coordinator._base_url}_salt_refill"

    async def async_press(self) -> None:
        """Handle the button press."""
        number_entity = self.hass.states.get(f"number.{DOMAIN}_salt_refill_mass")
        if not number_entity or not number_entity.state:
            raise ValueError("Salt refill mass not set")
        mass_kg = float(number_entity.state)
        mass_g = int(mass_kg * 1000)
        cmd = f"5600{mass_g:08x}"[:8]  # Ensure 4 bytes
        async with self._coordinator._session.get(
            f"{self._coordinator._base_url}{cmd}", auth=self._coordinator._auth
        ) as resp:
            resp.raise_for_status()
        await self._coordinator.async_request_refresh()

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._coordinator.last_update_success
