"""Config flow for Judo Connectivity Module integration."""
import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL

class JudoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Judo Connectivity Module."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                session = async_get_clientsession(self.hass)
                url = f"http://{user_input[CONF_HOST]}:{user_input[CONF_PORT]}/api/rest/FF00"
                auth = aiohttp.BasicAuth(user_input[CONF_USERNAME], user_input[CONF_PASSWORD])
                async with session.get(url, auth=auth, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    if "data" not in data:
                        raise ValueError("Invalid response from device")
            except (aiohttp.ClientError, ValueError) as err:
                errors["base"] = "cannot_connect" if isinstance(err, aiohttp.ClientError) else "invalid_auth"
            else:
                unique_id = f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Judo Device at {user_input[CONF_HOST]}",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=8080): int,
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            description_placeholders={
                "url": "e.g., 192.168.44.5",
                "port": "e.g., 8080",
                "username": "Your Judo username",
                "password": "Your Judo password",
            },
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return JudoOptionsFlow(config_entry)

class JudoOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=self.config_entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL),
                    ): vol.All(vol.Coerce(int), vol.Range(min=30)),
                }
            ),
        )
