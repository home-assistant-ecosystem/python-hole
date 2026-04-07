# import pytest and asyncio for async tests
import pytest
from unittest.mock import AsyncMock, MagicMock

import aiohttp

from hole.v5 import HoleV5
from hole.v6 import HoleV6
from hole import exceptions

# pytest-asyncio is required for async tests
pytestmark = pytest.mark.asyncio


class DummyResponse:
    """Dummy response class for simulating aiohttp responses."""

    def __init__(self, status=200, json_data=None, text_data=None):
        """Initialize the dummy response."""
        self.status = status
        self._json = json_data or {}
        self._text = text_data or "{}"

    async def json(self):
        """Return the JSON data."""
        return self._json

    async def text(self):
        """Return the text data."""
        return self._text


@pytest.fixture
def aiohttp_session():
    """Fixture for creating a mock aiohttp session."""
    return MagicMock(spec=aiohttp.ClientSession)


@pytest.mark.asyncio
async def test_v5_get_data_success(aiohttp_session):
    """Test successful data retrieval for HoleV5."""
    aiohttp_session.get = AsyncMock(
        return_value=DummyResponse(
            json_data={
                "status": "enabled",
                "unique_clients": 2,
                "unique_domains": 3,
                "ads_blocked_today": 4,
                "ads_percentage_today": 5.5,
                "clients_ever_seen": 6,
                "dns_queries_today": 7,
                "domains_being_blocked": 8,
                "queries_cached": 9,
                "queries_forwarded": 10,
            }
        )
    )
    hole5 = HoleV5("localhost", aiohttp_session, api_token="token")
    await hole5.get_data()
    assert hole5.status == "enabled"
    assert hole5.unique_clients == 2
    assert hole5.unique_domains == 3
    assert hole5.ads_blocked_today == 4
    assert hole5.ads_percentage_today == 5.5
    assert hole5.clients_ever_seen == 6
    assert hole5.dns_queries_today == 7
    assert hole5.domains_being_blocked == 8
    assert hole5.queries_cached == 9
    assert hole5.queries_forwarded == 10


@pytest.mark.asyncio
async def test_v5_get_data_connection_error(aiohttp_session):
    """Test connection error handling for HoleV5."""
    aiohttp_session.get = AsyncMock(side_effect=aiohttp.ClientError)
    hole5 = HoleV5("localhost", aiohttp_session, api_token="token")
    with pytest.raises(exceptions.HoleConnectionError):
        await hole5.get_data()


@pytest.mark.asyncio
async def test_v6_get_data_success(aiohttp_session):
    """Test successful data retrieval for HoleV6."""
    hole6 = HoleV6("localhost", aiohttp_session, password="pw")
    hole6.ensure_auth = AsyncMock()
    hole6._fetch_data = AsyncMock(
        side_effect=[
            {
                "queries": {
                    "blocked": 1,
                    "percent_blocked": 2.5,
                    "unique_domains": 3,
                    "total": 4,
                    "cached": 5,
                    "forwarded": 6,
                    "replies": {},
                },
                "clients": {"active": 2, "total": 3},
                "gravity": {"domains_being_blocked": 11},
            },
            {"domains": ["ad.com"]},
            {"domains": ["ok.com"]},
            {"clients": {"active": 2, "total": 3}},
            {"upstreams": ["8.8.8.8"]},
            {"blocking": "enabled"},
            {
                "core": {
                    "local": {"version": "1", "hash": "a"},
                    "remote": {"version": "2", "hash": "b"},
                },
                "web": {
                    "local": {"version": "1", "hash": "a"},
                    "remote": {"version": "2", "hash": "b"},
                },
                "ftl": {
                    "local": {"version": "1", "hash": "a"},
                    "remote": {"version": "2", "hash": "b"},
                },
            },
        ]
    )
    await hole6.get_data()
    assert hole6.ads_blocked_today == 1
    assert hole6.ads_percentage_today == 2.5
    assert hole6.unique_domains == 3
    assert hole6.dns_queries_today == 4
    assert hole6.queries_cached == 5
    assert hole6.queries_forwarded == 6
    assert hole6.top_ads == ["ad.com"]
    assert hole6.top_queries == ["ok.com"]
    assert hole6.unique_clients == 2
    assert hole6.clients_ever_seen == 3
    assert hole6.status == "enabled"
