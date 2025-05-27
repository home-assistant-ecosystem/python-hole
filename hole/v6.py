"""*hole API Python client."""

import asyncio
import socket
import json
import time
import logging
from typing import Optional, Literal

import aiohttp
import sys

if sys.version_info >= (3, 11):
    import asyncio as async_timeout
else:
    import async_timeout

from . import exceptions

_LOGGER = logging.getLogger(__name__)

_INSTANCE = "{protocol}://{host}{port_str}/{location}/api"


class HoleV6:
    """A class for handling connections with a Pi-hole instance."""

    def __init__(
        self,
        host: str,
        session: aiohttp.ClientSession,
        location: str = "admin",
        protocol: Literal["http", "https"] = "http",
        verify_tls: bool = True,
        password: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """Initialize the connection to a Pi-hole instance."""
        if protocol not in ["http", "https"]:
            raise exceptions.HoleError(
                f"Protocol {protocol} is invalid. Must be http or https"
            )

        self._session = session
        self.protocol = protocol
        self.verify_tls = verify_tls if protocol == "https" else False
        self.host = host
        self.location = location.strip("/")  # Remove any trailing slashes
        self.password = password
        self._session_id = None
        self._session_validity = None
        self._csrf_token = None

        # Set default ports if not specified
        if port is None:
            port = 443 if protocol == "https" else 80
        self.port = port

        # Initialize data containers
        self.data = {}
        self.blocked_domains = {}
        self.permitted_domains = {}
        self.clients = {}
        self.upstreams = {}
        self.blocking_status = {}
        self.versions = {}

        # Construct base URL
        if (protocol == "http" and port != 80) or (protocol == "https" and port != 443):
            self.base_url = f"{protocol}://{host}:{port}"
        else:
            self.base_url = f"{protocol}://{host}"

    async def authenticate(self):
        """Authenticate with Pi-hole and get session ID."""
        if not self.password:
            return

        # If we have an existing session, logout first
        if self._session_id:
            await self.logout()

        auth_url = f"{self.base_url}/api/auth"

        try:
            async with async_timeout.timeout(5):
                response = await self._session.post(
                    auth_url, json={"password": str(self.password)}, ssl=self.verify_tls
                )

                if response.status == 401:
                    raise exceptions.HoleError(
                        "Authentication failed: Invalid password"
                    )
                elif response.status == 400:
                    try:
                        error_data = json.loads(await response.text())
                        error_msg = error_data.get("error", {}).get(
                            "message", "Bad request"
                        )
                    except json.JSONDecodeError:
                        error_msg = "Bad request"
                    raise exceptions.HoleError(f"Authentication failed: {error_msg}")
                elif response.status != 200:
                    raise exceptions.HoleError(
                        f"Authentication failed with status {response.status}"
                    )

                try:
                    data = json.loads(await response.text())
                except json.JSONDecodeError as err:
                    raise exceptions.HoleError(f"Invalid JSON response: {err}")

                session_data = data.get("session", {})

                if not session_data.get("valid"):
                    raise exceptions.HoleError(
                        "Authentication unsuccessful: Invalid session"
                    )

                self._session_id = session_data.get("sid")
                if not self._session_id:
                    raise exceptions.HoleError(
                        "Authentication failed: No session ID received"
                    )

                # Store CSRF token if provided
                self._csrf_token = session_data.get("csrf")

                # Set session validity
                validity_seconds = session_data.get("validity", 300)
                self._session_validity = time.time() + validity_seconds

                _LOGGER.info("Successfully authenticated with Pi-hole")

        except (asyncio.TimeoutError, aiohttp.ClientError, socket.gaierror) as err:
            raise exceptions.HoleConnectionError(
                f"Cannot authenticate with Pi-hole: {err}"
            )

    async def logout(self):
        """Logout and cleanup the current session."""
        if not self._session_id:
            return

        logout_url = f"{self.base_url}/api/auth"
        headers = {"X-FTL-SID": self._session_id}

        try:
            async with async_timeout.timeout(5):
                await self._session.delete(
                    logout_url, headers=headers, ssl=self.verify_tls
                )
        finally:
            self._session_id = None
            self._session_validity = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.logout()

    async def ensure_auth(self):
        """Ensure we have a valid session."""
        if not self._session_id or (
            self._session_validity and time.time() > self._session_validity
        ):
            await self.authenticate()

    async def _fetch_data(self, endpoint: str, params=None) -> dict:
        """Fetch data from a specific API endpoint."""
        await self.ensure_auth()

        url = f"{self.base_url}/api{endpoint}"
        headers = {}

        if self._session_id:
            headers["X-FTL-SID"] = self._session_id
            if self._csrf_token:
                headers["X-FTL-CSRF"] = self._csrf_token

        try:
            async with async_timeout.timeout(5):
                response = await self._session.get(
                    url, params=params, headers=headers, ssl=self.verify_tls
                )

                if response.status == 401:
                    _LOGGER.info("Session expired, re-authenticating")
                    await self.authenticate()
                    if self._session_id:
                        headers["X-FTL-SID"] = self._session_id
                        if self._csrf_token:
                            headers["X-FTL-CSRF"] = self._csrf_token
                    response = await self._session.get(
                        url, params=params, headers=headers, ssl=self.verify_tls
                    )

                if response.status != 200:
                    raise exceptions.HoleError(
                        f"Failed to fetch data: {response.status}"
                    )

                return await response.json()

        except (asyncio.TimeoutError, aiohttp.ClientError, socket.gaierror) as err:
            raise exceptions.HoleConnectionError(
                f"Cannot fetch data from Pi-hole: {err}"
            )

    async def get_data(self):
        """Get comprehensive data from Pi-hole instance."""
        await self.ensure_auth()

        # Fetch all required data
        self.data = await self._fetch_data("/stats/summary")
        self.blocked_domains = await self._fetch_data(
            "/stats/top_domains", {"blocked": "true", "count": 10}
        )
        self.permitted_domains = await self._fetch_data(
            "/stats/top_domains", {"blocked": "false", "count": 10}
        )
        self.clients = await self._fetch_data("/stats/top_clients", {"count": 10})
        self.upstreams = await self._fetch_data("/stats/upstreams")
        self.blocking_status = await self._fetch_data("/dns/blocking")
        await self.get_versions()

    async def get_versions(self):
        """Get version information from Pi-hole."""
        await self.ensure_auth()
        response = await self._fetch_data("/info/version")
        self.versions = response.get("version", {})

    async def enable(self):
        """Enable DNS blocking."""
        if not self.password:
            raise exceptions.HoleError(
                "Password required for enable/disable operations"
            )

        await self.ensure_auth()
        url = f"{self.base_url}/api/dns/blocking"
        headers = {"X-FTL-SID": self._session_id}
        if self._csrf_token:
            headers["X-FTL-CSRF"] = self._csrf_token

        payload = {"blocking": True, "timer": None}

        try:
            async with async_timeout.timeout(5):
                response = await self._session.post(
                    url, json=payload, headers=headers, ssl=self.verify_tls
                )

                if response.status != 200:
                    raise exceptions.HoleError(
                        f"Failed to enable blocking: {response.status}"
                    )

                # Wait for status to be enabled
                retries = 0
                while retries < 10:  # Maximum 10 retries
                    await self.get_data()
                    if self.status == "enabled":
                        break
                    retries += 1
                    await asyncio.sleep(0.1)

                _LOGGER.info("Successfully enabled Pi-hole blocking")
                return await response.json()

        except (asyncio.TimeoutError, aiohttp.ClientError, socket.gaierror) as err:
            raise exceptions.HoleConnectionError(f"Cannot enable blocking: {err}")

    async def disable(self, duration=0):
        """Disable DNS blocking.

        Args:
            duration: Number of seconds to disable blocking for. If 0, disable indefinitely.
        """
        if not self.password:
            raise exceptions.HoleError(
                "Password required for enable/disable operations"
            )

        await self.ensure_auth()
        url = f"{self.base_url}/api/dns/blocking"
        headers = {"X-FTL-SID": self._session_id}
        if self._csrf_token:
            headers["X-FTL-CSRF"] = self._csrf_token

        payload = {"blocking": False, "timer": duration if duration > 0 else None}

        try:
            async with async_timeout.timeout(5):
                response = await self._session.post(
                    url, json=payload, headers=headers, ssl=self.verify_tls
                )

                if response.status != 200:
                    raise exceptions.HoleError(
                        f"Failed to disable blocking: {response.status}"
                    )

                # Wait for status to be disabled
                retries = 0
                while retries < 10:  # Maximum 10 retries
                    await self.get_data()
                    if self.status == "disabled":
                        break
                    retries += 1
                    await asyncio.sleep(0.1)

                _LOGGER.info(
                    "Successfully disabled Pi-hole blocking%s",
                    f" for {duration} seconds" if duration > 0 else "",
                )
                return await response.json()

        except (asyncio.TimeoutError, aiohttp.ClientError, socket.gaierror) as err:
            raise exceptions.HoleConnectionError(f"Cannot disable blocking: {err}")

    # Properties for accessing the data
    @property
    def status(self) -> str:
        """Return the status of the Pi-hole instance."""
        return self.blocking_status.get("blocking", "unknown")

    @property
    def unique_clients(self) -> int:
        """Return the number of unique clients."""
        return self.data.get("clients", {}).get("active", 0)

    @property
    def unique_domains(self) -> int:
        """Return the number of unique domains."""
        return self.data.get("queries", {}).get("unique_domains", 0)

    @property
    def ads_blocked_today(self) -> int:
        """Return the number of ads blocked today."""
        return self.data.get("queries", {}).get("blocked", 0)

    @property
    def ads_percentage_today(self) -> float:
        """Return the percentage of ads blocked today."""
        return self.data.get("queries", {}).get("percent_blocked", 0)

    @property
    def clients_ever_seen(self) -> int:
        """Return the number of clients ever seen."""
        return self.data.get("clients", {}).get("total", 0)

    @property
    def dns_queries_today(self) -> int:
        """Return the number of DNS queries today."""
        return self.data.get("queries", {}).get("total", 0)

    @property
    def domains_being_blocked(self) -> int:
        """Return the number of domains being blocked."""
        return self.data.get("gravity", {}).get("domains_being_blocked", 0)

    @property
    def queries_cached(self) -> int:
        """Return the number of queries cached."""
        return self.data.get("queries", {}).get("cached", 0)

    @property
    def queries_forwarded(self) -> int:
        """Return the number of queries forwarded."""
        return self.data.get("queries", {}).get("forwarded", 0)

    @property
    def core_current(self) -> str:
        """Return current core version."""
        return self.versions.get("core", {}).get("local", {}).get("version")

    @property
    def core_latest(self) -> str:
        """Return latest available core version."""
        return self.versions.get("core", {}).get("remote", {}).get("version")

    @property
    def core_update(self) -> bool:
        """Return whether a core update is available."""
        local = self.versions.get("core", {}).get("local", {}).get("hash")
        remote = self.versions.get("core", {}).get("remote", {}).get("hash")
        return local != remote if local and remote else False

    @property
    def web_current(self) -> str:
        """Return current web interface version."""
        return self.versions.get("web", {}).get("local", {}).get("version")

    @property
    def web_latest(self) -> str:
        """Return latest available web interface version."""
        return self.versions.get("web", {}).get("remote", {}).get("version")

    @property
    def web_update(self) -> bool:
        """Return whether a web interface update is available."""
        local = self.versions.get("web", {}).get("local", {}).get("hash")
        remote = self.versions.get("web", {}).get("remote", {}).get("hash")
        return local != remote if local and remote else False

    @property
    def ftl_current(self) -> str:
        """Return current FTL version."""
        return self.versions.get("ftl", {}).get("local", {}).get("version")

    @property
    def ftl_latest(self) -> str:
        """Return latest available FTL version."""
        return self.versions.get("ftl", {}).get("remote", {}).get("version")

    @property
    def ftl_update(self) -> bool:
        """Return whether an FTL update is available."""
        local = self.versions.get("ftl", {}).get("local", {}).get("hash")
        remote = self.versions.get("ftl", {}).get("remote", {}).get("hash")
        return local != remote if local and remote else False

    @property
    def top_queries(self) -> list:
        """Return the list of top permitted domains."""
        return self.permitted_domains.get("domains", [])

    @property
    def top_ads(self) -> list:
        """Return the list of top blocked domains."""
        return self.blocked_domains.get("domains", [])

    @property
    def forward_destinations(self) -> list:
        """Return the list of forward destinations."""
        return self.upstreams.get("upstreams", [])

    @property
    def reply_types(self) -> dict:
        """Return the dictionary of reply types."""
        return self.data.get("queries", {}).get("replies", {})
