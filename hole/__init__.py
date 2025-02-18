"""*hole API Python client."""
import asyncio
import logging
import socket

import aiohttp
import async_timeout

from . import exceptions

_LOGGER = logging.getLogger(__name__)
_INSTANCE = "{schema}://{host}/{location}/api.php"


class Hole(object):
    """A class for handling connections with a *hole instance."""

    def __init__(
        self,
        host,
        session,
        location="api",
        tls=False,
        verify_tls=True,
        api_token=None,
    ):
        """Initialize the connection to a *hole instance."""
        self._session = session
        self.tls = tls
        self.verify_tls = verify_tls
        self.schema = "https" if self.tls else "http"
        self.host = host
        self.location = location
        self.api_token = api_token
        self.data = {}
        self.versions = {}
        self.base_url = _INSTANCE.format(
            schema=self.schema, host=self.host, location=self.location
        )

    async def _request(self, params):
        """Helper method to make API requests with fallback."""
        for location in ["api", "admin"]:
            self.base_url = _INSTANCE.format(
                schema=self.schema, host=self.host, location=location
            )
            try:
                async with async_timeout.timeout(5):
                    response = await self._session.get(self.base_url, params=params)
                
                if response.status == 200:
                    return await response.json()
            except (asyncio.TimeoutError, aiohttp.ClientError, socket.gaierror):
                _LOGGER.warning("Failed to connect using location '%s', trying fallback...", location)
                continue
        msg = "Cannot load data from *hole: {}".format(self.host)
        _LOGGER.error(msg)
        raise exceptions.HoleConnectionError(msg)

    async def get_data(self):
        """Get details of a *hole instance."""
        params = "summaryRaw&auth={}".format(self.api_token)
        self.data = await self._request(params)
        _LOGGER.debug(self.data)

    async def get_versions(self):
        """Get version information of a *hole instance."""
        params = "versions"
        self.versions = await self._request(params)
        _LOGGER.debug(self.versions)

    async def enable(self):
        """Enable DNS blocking on a *hole instance."""
        if self.api_token is None:
            _LOGGER.error("You need to supply an api_token to use this")
            return
        params = "enable=True&auth={}".format(self.api_token)
        await self._request(params)
        while self.status != "enabled":
            _LOGGER.debug("Awaiting status to be enabled")
            await self.get_data()
            await asyncio.sleep(0.01)

    async def disable(self, duration=True):
        """Disable DNS blocking on a *hole instance."""
        if self.api_token is None:
            _LOGGER.error("You need to supply an api_token to use this")
            return
        params = "disable={}&auth={}".format(duration, self.api_token)
        await self._request(params)
        while self.status != "disabled":
            _LOGGER.debug("Awaiting status to be disabled")
            await self.get_data()
            await asyncio.sleep(0.01)

    @property
    def status(self):
        """Return the status of the *hole instance."""
        return self.data.get("status")

    @property
    def unique_clients(self):
        """Return the unique clients of the *hole instance."""
        return self.data.get("unique_clients")

    @property
    def unique_domains(self):
        """Return the unique domains of the *hole instance."""
        return self.data.get("unique_domains")

    @property
    def ads_blocked_today(self):
        """Return the ads blocked today of the *hole instance."""
        return self.data.get("ads_blocked_today")

    @property
    def ads_percentage_today(self):
        """Return the ads percentage today of the *hole instance."""
        return self.data.get("ads_percentage_today")

    @property
    def clients_ever_seen(self):
        """Return the clients_ever_seen of the *hole instance."""
        return self.data.get("clients_ever_seen")

    @property
    def dns_queries_today(self):
        """Return the dns queries today of the *hole instance."""
        return self.data.get("dns_queries_today")

    @property
    def domains_being_blocked(self):
        """Return the domains being blocked of the *hole instance."""
        return self.data.get("domains_being_blocked")

    @property
    def queries_cached(self):
        """Return the queries cached of the *hole instance."""
        return self.data.get("queries_cached")

    @property
    def queries_forwarded(self):
        """Return the queries forwarded of the *hole instance."""
        return self.data.get("queries_forwarded")

    @property
    def ftl_current(self):
        return self.versions.get("FTL_current")

    @property
    def ftl_latest(self):
        return self.versions.get("FTL_latest")

    @property
    def ftl_update(self):
        return self.versions.get("FTL_update")

    @property
    def core_current(self):
        return self.versions.get("core_current")

    @property
    def core_latest(self):
        return self.versions.get("core_latest")

    @property
    def core_update(self):
        return self.versions.get("core_update")

    @property
    def web_current(self):
        return self.versions.get("web_current")

    @property
    def web_latest(self):
        return self.versions.get("web_latest")

    @property
    def web_update(self):
        return self.versions.get("web_update")
