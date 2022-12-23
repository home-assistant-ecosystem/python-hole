"""Example for the usage of the hole module."""
import asyncio
import json

import aiohttp

from hole import Hole

API_TOKEN = "YOUR_API_TOKEN"


async def main():
    """Get the data from a *hole instance."""
    async with aiohttp.ClientSession() as session:
        data = Hole("192.168.0.215", session)

        await data.get_versions()
        print(json.dumps(data.versions, indent=4, sort_keys=True))
        print(
            "Version:",
            data.core_current,
            "Latest:",
            data.core_latest,
            "Update available:",
            data.core_update,
        )
        print(
            "FTL:",
            data.ftl_current,
            "Latest:",
            data.ftl_latest,
            "Update available:",
            data.ftl_update,
        )
        print(
            "Web:",
            data.web_current,
            "Latest:",
            data.web_latest,
            "Update available:",
            data.web_update,
        )

        await data.get_data()

        # Get the raw data
        print(json.dumps(data.data, indent=4, sort_keys=True))

        print("Status:", data.status)
        print("Domains being blocked:", data.domains_being_blocked)


async def disable():
    """Get the data from a *hole instance."""
    async with aiohttp.ClientSession() as session:
        data = Hole("192.168.0.215", session, api_token=API_TOKEN)
        await data.disable()


async def enable():
    """Get the data from a *hole instance."""
    async with aiohttp.ClientSession() as session:
        data = Hole("192.168.0.215", session, api_token=API_TOKEN)
        await data.enable()


if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(disable())
    asyncio.run(enable())
