"""
Copyright (c) 2018 Fabian Affolter <fabian@affolter-engineering.ch>

Licensed under MIT. All rights reserved.
"""
import asyncio
import json

import aiohttp

from hole import Hole


async def main():
    """Get the data from a *hole instance."""
    async with aiohttp.ClientSession() as session:
        data = Hole('192.168.0.215', loop, session)
        await data.get_data()

        # Get the raw data
        print(json.dumps(data.data, indent=4, sort_keys=True))

        print("Status:", data.status)
        print("Domains being blocked:", data.domains_being_blocked)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())

