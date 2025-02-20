"""Config flow for Judo Connectivity Module integration."""

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_PORT, CONF_UPDATE_INTERVAL, CONF_URL, DOMAIN
from .judo import JudoClient


class JudoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Judo Connectivity Module."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Test connection
            client = JudoClient(
                user_input[CONF_URL],
                user_input[CONF_PORT],
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
            )
            try:
                await client.async_fetch_data("FF00")  # Test with device type
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            else:
                # Ensure unique entry
                await self.async_set_unique_id(
                    f"{user_input[CONF_URL]}:{user_input[CONF_PORT]}"
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Judo at {user_input[CONF_URL]}:{user_input[CONF_PORT]}",
                    data=user_input,
                    options={CONF_UPDATE_INTERVAL: user_input[CONF_UPDATE_INTERVAL]},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_URL, description={"suggested_value": "http://192.168.1.x"}
                    ): str,
                    vol.Required(CONF_PORT, default=8080): int,
                    vol.Required(
                        CONF_USERNAME, description={"suggested_value": "admin"}
                    ): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Required(CONF_UPDATE_INTERVAL, default=300): int,
                }
            ),
            errors=errors,
        )

    async def async_step_import(self, import_info: dict[str, any]) -> FlowResult:
        """Handle import from configuration.yaml (not implemented)."""
        return await self.async_step_user(import_info)
