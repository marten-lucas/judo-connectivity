"""Sensor entities for Judo Connectivity Module."""

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfMass, UnitOfVolume, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEVICE_TYPES, DOMAIN
from .coordinator import JudoDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: JudoDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        JudoDeviceTypeSensor(coordinator, entry),
        JudoDeviceNumberSensor(coordinator, entry),
        JudoSoftwareVersionSensor(coordinator, entry),
        JudoOperatingHoursSensor(coordinator, entry),
        JudoTotalWaterVolumeSensor(coordinator, entry),
        JudoSaltRangeSensor(coordinator, entry),
        JudoSaltStockSensor(coordinator, entry),
        JudoWaterHardnessSensor(coordinator, entry),
    ]
    async_add_entities(entities)


class JudoSensor(SensorEntity):
    """Base class for Judo sensors."""

    def __init__(
        self, coordinator: JudoDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._entry = entry
        self._attr_has_entity_name = True
        self._attr_unique_id = (
            f"{entry.unique_id}_{self._attr_name.lower().replace(' ', '_')}"
        )

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


class JudoDeviceTypeSensor(JudoSensor):
    """Representation of the Device Type sensor."""

    _attr_name = "Device Type"
    _attr_icon = "mdi:water-pump"

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        hex_value = self.coordinator.data["device_type"]
        value = int(hex_value, 16)
        return DEVICE_TYPES.get(value, "Unknown")


class JudoDeviceNumberSensor(JudoSensor):
    """Representation of the Device Number sensor."""

    _attr_name = "Device Number"
    _attr_icon = "mdi:numeric"

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        hex_value = self.coordinator.data["device_no"]
        return str(int(hex_value, 16))


class JudoSoftwareVersionSensor(JudoSensor):
    """Representation of the Software Version sensor."""

    _attr_name = "Software Version"
    _attr_icon = "mdi:chip"

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        hex_value = self.coordinator.data["sw_version"]
        bytes_value = bytes.fromhex(hex_value)
        return f"{bytes_value[1]}.{bytes_value[2]:02d}"


class JudoOperatingHoursSensor(JudoSensor):
    """Representation of the Operating Hours sensor."""

    _attr_name = "Operating Hours"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.HOURS
    _attr_icon = "mdi:clock"

    @property
    def state(self) -> float:
        """Return the state of the sensor."""
        hex_value = self.coordinator.data["operating_hours"]
        bytes_value = bytes.fromhex(hex_value)
        minutes, hours, days = (
            bytes_value[0],
            bytes_value[1],
            int.from_bytes(bytes_value[2:], "little"),
        )
        return round(days * 24 + hours + minutes / 60, 1)


class JudoTotalWaterVolumeSensor(JudoSensor):
    """Representation of the Total Water Volume sensor."""

    _attr_name = "Total Water Volume"
    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS
    _attr_icon = "mdi:water"

    @property
    def state(self) -> float:
        """Return the state of the sensor."""
        hex_value = self.coordinator.data["total_water_volume"]
        reordered_hex = (
            hex_value[6:8] + hex_value[4:6] + hex_value[2:4] + hex_value[0:2]
        )
        liters = liters = int(reordered_hex, 16)
        return liters / 1000  # Liters to m³


class JudoSaltRangeSensor(JudoSensor):
    """Representation of the Regeneration Salt Range sensor."""

    _attr_name = "Regeneration Salt Range"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.DAYS
    _attr_icon = "mdi:clock-outline"

    @property
    def state(self) -> int:
        """Return the state of the sensor."""
        hex_value = self.coordinator.data["salt_range"]
        bytes_value = bytes.fromhex(hex_value)
        return int.from_bytes(bytes_value[2:], "little")


class JudoSaltStockSensor(JudoSensor):
    """Representation of the Regeneration Salt Stock sensor."""

    _attr_name = "Regeneration Salt Stock"
    _attr_device_class = SensorDeviceClass.WEIGHT
    _attr_native_unit_of_measurement = UnitOfMass.GRAMS
    _attr_icon = "mdi:weight"

    @property
    def state(self) -> int:
        """Return the state of the sensor."""
        hex_value = self.coordinator.data["salt_stock"]
        bytes_value = bytes.fromhex(hex_value)
        return int.from_bytes(bytes_value[:2], "little")


class JudoWaterHardnessSensor(JudoSensor):
    """Representation of the Water Hardness sensor."""

    _attr_name = "Water Hardness"
    _attr_native_unit_of_measurement = "°dH"
    _attr_icon = "mdi:water-opacity"

    @property
    def state(self) -> int:
        """Return the state of the sensor."""
        hex_value = self.coordinator.data["water_hardness"]
        bytes_value = bytes.fromhex(hex_value)
        return bytes_value[0]  # LSB
