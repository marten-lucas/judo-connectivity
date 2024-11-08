"""Setup for IP, username, and password for the Judo Connectivity Module."""

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_IP_ADDRESS, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback

from .const import DOMAIN
from .judo import JudoAPI

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_IP_ADDRESS): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class JudoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for setting up the Judo Connectivity Module."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Return the options flow for this handler."""
        return JudoOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initiated by the user."""
        errors = {}
        if user_input is not None:
            ip = user_input[CONF_IP_ADDRESS]
            user = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]
            try:
                judo_connection = JudoAPI(ip, user, password)
                info = await judo_connection.test()

                if info:
                    return self.async_create_entry(
                        title="Judo Connectivity Module", data=user_input
                    )
                errors["base"] = "device_not_found"
            except aiohttp.ClientError:
                _LOGGER.error("Failed to connect to device at %s", ip)
                errors["base"] = "connection_error"
            except Exception as ex:  # Catching general exceptions for unknown errors
                _LOGGER.error("Unexpected error: %s", ex)
                errors["base"] = "unknown_error"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class JudoOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for the Judo Connectivity Module."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow handler."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle options for Judo connectivity."""
        if user_input is not None:
            # Save the options if submitted by the user
            return self.async_create_entry(title="", data=user_input)

        # Populate the schema with existing config values as default values
        current_data = self.config_entry.data
        options_schema = vol.Schema(
            {
                vol.Required(
                    CONF_IP_ADDRESS, default=current_data.get(CONF_IP_ADDRESS)
                ): str,
                vol.Required(
                    CONF_USERNAME, default=current_data.get(CONF_USERNAME)
                ): str,
                vol.Required(
                    CONF_PASSWORD, default=current_data.get(CONF_PASSWORD)
                ): str,
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)
