"""The Judo Connectivity Module integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr

from .const import CONF_PORT, CONF_UPDATE_INTERVAL, CONF_URL, DOMAIN
from .coordinator import JudoDataUpdateCoordinator
from .judo import JudoClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BUTTON, Platform.NUMBER, Platform.SENSOR]

type JudoConfigEntry = ConfigEntry[JudoDataUpdateCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: JudoConfigEntry) -> bool:
    """Set up Judo Connectivity Module from a config entry."""
    url = entry.data[CONF_URL]
    port = entry.data[CONF_PORT]
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    update_interval = entry.options.get(CONF_UPDATE_INTERVAL, 300)  # Default 5 min

    # 1. Create API instance
    client = JudoClient(url, port, username, password)
    coordinator = JudoDataUpdateCoordinator(hass, client, update_interval)

    # 2. Validate the API connection
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady(f"Failed to connect to Judo device: {err}") from err

    # 3. Store coordinator in runtime data
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    entry.runtime_data = coordinator

    # Register device in device registry
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, f"{url}:{port}")},
        manufacturer="Judo",
        name="Judo Connectivity Module",
        model=coordinator.data["device_type"],
        sw_version=coordinator.data["sw_version"],
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: JudoConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok and entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
