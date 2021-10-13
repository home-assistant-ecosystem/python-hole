"""
Copyright (c) 2018 Fabian Affolter <fabian@affolter-engineering.ch>

Licensed under MIT. All rights reserved.
"""
import asyncio
import json

import aiohttp

from hole import Hole

API_TOKEN = "YOUR_API_TOKEN"


async def main():
    """Get the data from a *hole instance."""
    async with aiohttp.ClientSession() as session:
        data = Hole("192.168.0.215", loop, session)

        await data.get_versions()
        print(json.dumps(data.versions, indent=4, sort_keys=True))
        print("Version:", data.core_current, "Latest:", data.core_latest, "Update available:", data.core_update)
        print("FTL:", data.ftl_current, "Latest:", data.ftl_latest, "Update available:", data.ftl_update)
        print("Web:", data.web_current, "Latest:", data.web_latest, "Update available:", data.web_update)

        await data.get_data()

        # Get the raw data
        print(json.dumps(data.data, indent=4, sort_keys=True))

        print("Status:", data.status)
        print("Domains being blocked:", data.domains_being_blocked)


async def disable():
    """Get the data from a *hole instance."""
    async with aiohttp.ClientSession() as session:
        data = Hole("192.168.0.215", loop, session, api_token=API_TOKEN)
        await data.disable()


async def enable():
    """Get the data from a *hole instance."""
    async with aiohttp.ClientSession() as session:
        data = Hole("192.168.0.215", loop, session, api_token=API_TOKEN)
        await data.enable()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_until_complete(disable())
loop.run_until_complete(enable())
