"""Number platform for Judo Connectivity Module."""
from homeassistant.components.number import NumberEntity, NumberDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfMass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import JudoDataUpdateCoordinator

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Judo number entity."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    device_info = DeviceInfo(
        identifiers={(DOMAIN, f"{entry.data['host']}:{entry.data['port']}")},
        name=f"Judo Device at {entry.data['host']}",
        manufacturer="Judo",
    )
    async_add_entities([JudoSaltRefillMass(coordinator, device_info)])

class JudoSaltRefillMass(NumberEntity):
    """Number entity for salt refill mass."""

    _attr_name = "Regeneration Salt Refill Mass"
    _attr_has_entity_name = True
    _attr_device_class = NumberDeviceClass.MASS
    _attr_native_unit_of_measurement = UnitOfMass.KILOGRAMS
    _attr_native_min_value = 0.5
    _attr_native_max_value = 25.0
    _attr_native_step = 0.5
    _attr_translation_key = "salt_refill_mass"

    def __init__(self, coordinator: JudoDataUpdateCoordinator, device_info: DeviceInfo):
        """Initialize the number entity."""
        self._coordinator = coordinator
        self._attr_device_info = device_info
        self._attr_unique_id = f"{coordinator._base_url}_salt_refill_mass"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._coordinator.last_update_success

    async def async_set_native_value(self, value: float) -> None:
        """Set the value (no API call here, just store locally)."""
        self._attr_native_value = value
        self.async_write_ha_state()
