"""Number entity for Judo Connectivity Module."""

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfMass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import JudoDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    coordinator: JudoDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([JudoSaltRefillMassNumber(coordinator, entry)])


class JudoSaltRefillMassNumber(NumberEntity):
    """Representation of the Regeneration Salt Refill Mass number."""

    _attr_name = "Regeneration Salt Refill Mass"
    _attr_device_class = "mass"
    _attr_unit_of_measurement = UnitOfMass.KILOGRAMS
    _attr_icon = "mdi:scale"
    _attr_native_min_value = 0.5
    _attr_native_max_value = 25.0
    _attr_native_step = 0.5

    def __init__(
        self, coordinator: JudoDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the number entity."""
        self.coordinator = coordinator
        self._entry = entry
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{entry.unique_id}_regeneration_salt_refill_mass"
        self._attr_native_value = 5.0  # Default value

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

    async def async_set_native_value(self, value: float) -> None:
        """Set the value (not directly triggering API here)."""
        self._attr_native_value = value
        self.async_write_ha_state()
