"""Judo Connectivity Module API client."""

import aiohttp


class JudoClient:
    """Client to interact with Judo Connectivity Module API."""

    def __init__(self, url: str, port: int, username: str, password: str) -> None:
        """Initialize the client."""
        self.base_url = f"{url}:{port}/api/rest"
        self.auth = aiohttp.BasicAuth(username, password)

    async def async_fetch_data(self, command: str) -> str:
        """Fetch data from the Judo API."""
        async with (
            aiohttp.ClientSession() as session,
            session.get(f"{self.base_url}/{command}", auth=self.auth) as resp,
        ):
            resp.raise_for_status()
            data = await resp.json()
            return data["data"]

    async def async_set_salt_refill(self, mass_grams: int) -> None:
        """Set the salt refill mass."""
        hex_mass = f"{mass_grams:08x}"
        command = f"5600{hex_mass}"
        async with (
            aiohttp.ClientSession() as session,
            session.get(f"{self.base_url}/{command}", auth=self.auth) as resp,
        ):
            resp.raise_for_status()
