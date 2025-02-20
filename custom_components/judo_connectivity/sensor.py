"""Sensor platform for Judo Connectivity Module."""
import logging
from typing import Optional

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfMass, UnitOfTime, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import JudoDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

DEVICE_TYPE_MAP = {
    "34": "SOFTwell P",
    "35": "SOFTwell S",
    "36": "SOFTwell K",
    "47": "SOFTwell KP",
    "48": "SOFTwell KS",
}

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Judo sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    device_info = DeviceInfo(
        identifiers={(DOMAIN, f"{entry.data['host']}:{entry.data['port']}")},
        name=f"Judo Device at {entry.data['host']}",
        manufacturer="Judo",
    )
    entities = [
        JudoTextSensor(coordinator, "device_type", "Device Type", "FF00", device_info, translation="Gerätetyp"),
        JudoTextSensor(coordinator, "device_no", "Device Number", "0600", device_info, translation="Gerätenummer"),
        JudoTextSensor(coordinator, "sw_version", "Software Version", "0100", device_info, translation="Software-Version"),
        JudoOperatingHoursSensor(coordinator, device_info),
        JudoTotalWaterVolumeSensor(coordinator, device_info),
        JudoSaltRangeSensor(coordinator, device_info),
        JudoSaltStockSensor(coordinator, device_info),
        JudoWaterHardnessSensor(coordinator, device_info),
    ]
    async_add_entities(entities)

class JudoBaseSensor(SensorEntity):
    """Base class for Judo sensors."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: JudoDataUpdateCoordinator, device_info: DeviceInfo):
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_device_info = device_info
        self._attr_unique_id = f"{coordinator._base_url}_{self._attr_name}"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._coordinator.last_update_success

class JudoTextSensor(JudoBaseSensor):
    """Text sensor for Judo device."""

    def __init__(
        self,
        coordinator: JudoDataUpdateCoordinator,
        entity_id: str,
        name: str,
        command: str,
        device_info: DeviceInfo,
        translation: str,
    ):
        """Initialize the text sensor."""
        super().__init__(coordinator, device_info)
        self._attr_name = name
        self._attr_unique_id = f"{coordinator._base_url}_{entity_id}"
        self._command = command
        self._attr_translation_key = entity_id

    @property
    def state(self) -> Optional[str]:
        """Return the state of the sensor."""
        data = self._coordinator.data.get(self._command, "")
        if not data:
            return None
        if self._command == "FF00":
            return DEVICE_TYPE_MAP.get(data, "Unknown")
        if self._command == "0600":
            return str(int(data, 16))
        if self._command == "0100":
            ver = int(data, 16)
            return f"{ver // 100}.{ver % 100:02d}"
        return data

class JudoOperatingHoursSensor(JudoBaseSensor):
    """Operating hours sensor."""

    _attr_name = "Operating Hours"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.HOURS
    _attr_translation_key = "operating_hours"

    def __init__(self, coordinator: JudoDataUpdateCoordinator, device_info: DeviceInfo):
        """Initialize the sensor."""
        super().__init__(coordinator, device_info)

    @property
    def native_value(self) -> Optional[float]:
        """Return the operating hours."""
        data = self._coordinator.data.get("2500", "")
        if not data or len(data) < 8:
            return None
        minutes = int(data[0:2], 16)
        hours = int(data[2:4], 16)
        days = int(data[4:8], 16)
        return days * 24 + hours + minutes / 60.0

class JudoTotalWaterVolumeSensor(JudoBaseSensor):
    """Total water volume sensor."""

    _attr_name = "Total Water Volume"
    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS
    _attr_translation_key = "total_water_volume"

    def __init__(self, coordinator: JudoDataUpdateCoordinator, device_info: DeviceInfo):
        """Initialize the sensor."""
        super().__init__(coordinator, device_info)

    @property
    def native_value(self) -> Optional[float]:
        """Return the total water volume."""
        data = self._coordinator.data.get("2800", "")
        if not data or len(data) < 8:
            return None
        return int(data, 16) / 1000.0

class JudoSaltRangeSensor(JudoBaseSensor):
    """Salt range sensor."""

    _attr_name = "Regeneration Salt Range"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.DAYS
    _attr_translation_key = "salt_range"

    def __init__(self, coordinator: JudoDataUpdateCoordinator, device_info: DeviceInfo):
        """Initialize the sensor."""
        super().__init__(coordinator, device_info)

    @property
    def native_value(self) -> Optional[int]:
        """Return the salt range in days."""
        data = self._coordinator.data.get("5600", "")
        if not data or len(data) < 8:
            return None
        return int(data[4:8], 16)

class JudoSaltStockSensor(JudoBaseSensor):
    """Salt stock sensor."""

    _attr_name = "Regeneration Salt Stock"
    _attr_device_class = SensorDeviceClass.MASS
    _attr_native_unit_of_measurement = UnitOfMass.KILOGRAMS
    _attr_translation_key = "salt_stock"

    def __init__(self, coordinator: JudoDataUpdateCoordinator, device_info: DeviceInfo):
        """Initialize the sensor."""
        super().__init__(coordinator, device_info)

    @property
    def native_value(self) -> Optional[float]:
        """Return the salt stock in kg."""
        data = self._coordinator.data.get("5600", "")
        if not data or len(data) < 8:
            return None
        return int(data[0:4], 16) / 1000.0

class JudoWaterHardnessSensor(JudoBaseSensor):
    """Water hardness sensor."""

    _attr_name = "Water Hardness"
    _attr_native_unit_of_measurement = "°dH"
    _attr_translation_key = "water_hardness"

    def __init__(self, coordinator: JudoDataUpdateCoordinator, device_info: DeviceInfo):
        """Initialize the sensor."""
        super().__init__(coordinator, device_info)

    @property
    def native_value(self) -> Optional[int]:
        """Return the water hardness."""
        data = self._coordinator.data.get("5100", "")
        if not data or len(data) < 4:
            return None
        return int(data, 16)
