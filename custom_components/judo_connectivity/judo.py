"""Module for connecting to Judo Connectivity Module via REST API.

This module provides a client for interacting with the Judo water treatment system's
REST API, allowing for monitoring and control of the device.
"""

import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class JudoAPI:
    """Client for interacting with the Judo Connectivity Module REST API.

    Provides methods for querying device status and retrieving measurement data
    through authenticated HTTP requests.
    """

    def __init__(self, ip: str, username: str, password: str) -> None:
        """Initialize the JudoAPI client.

        Args:
            ip: IP address of the Judo device
            username: Authentication username
            password: Authentication password

        """
        self.base_url = f"http://{ip}/api/rest"
        self.auth = aiohttp.BasicAuth(username, password)

    async def call(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """Make a GET request to the specified API endpoint.

        Args:
            endpoint: The API endpoint to call
            params: Optional query parameters to include in the request

        Returns:
            JSON response data if the request is successful, None if an error occurs

        """
        if params is None:
            params = {}

        try:
            async with (
                aiohttp.ClientSession(auth=self.auth) as session,
                session.get(self.base_url + endpoint, params=params) as resp,
            ):
                resp.raise_for_status()
                return await resp.json(content_type=None)

        except aiohttp.ClientError as err:
            _LOGGER.error("Failed to call endpoint %s: %s", endpoint, err)
            return None

    async def test(self) -> bool:
        """Test connectivity to the device.

        Returns:
            True if connection is successful and device responds correctly,
            False otherwise

        """
        result = await self.call("/FF00")
        if result:
            raw_data = result.get("data", "")
            return raw_data == "47"
        return False

    async def get_soft_water_volume(self) -> float | None:
        """Retrieve the soft water volume from the device.

        Returns:
            The soft water volume in cubic meters (m³), or None if retrieval fails

        """
        response = await self.call("/2900")
        if response:
            raw_data = response.get("data", "")
            if len(raw_data) >= 8:
                value = int(
                    raw_data[6:8] + raw_data[4:6] + raw_data[2:4] + raw_data[0:2], 16
                )
                return value / 1000  # Convert to m³
        return None