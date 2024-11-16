"""The JudoApi Connectivity Module integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS, CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .judo import JudoAPI

PLATFORMS: list[Platform] = [Platform.BUTTON, Platform.NUMBER, Platform.SENSOR]
LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up JudoApi Connectivity Module from a config entry."""
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = JudoAPI(
        entry.data[CONF_IP_ADDRESS],
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
