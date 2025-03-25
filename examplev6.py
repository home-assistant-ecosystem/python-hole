"""Example for the usage of the hole module."""

import asyncio
import json
from datetime import datetime

import aiohttp

from hole import Hole

PASSWORD = "your_password_here"
HOST = "your_host_here"
PROTOCOL = "https"
PORT = 443
VERIFY_TLS = False


async def main():
    """Get the data from a Pi-hole instance."""
    async with aiohttp.ClientSession() as session:
        async with Hole(
            host=HOST,
            session=session,
            password=PASSWORD,
            protocol=PROTOCOL,
            port=PORT,
            verify_tls=VERIFY_TLS,
        ) as pihole:
            await pihole.get_data()

            print("\n=== Version Information ===")
            print(
                f"Core Version: {pihole.core_current} (Latest: {pihole.core_latest}, Update Available: {pihole.core_update})"
            )
            print(
                f"Web Version: {pihole.web_current} (Latest: {pihole.web_latest}, Update Available: {pihole.web_update})"
            )
            print(
                f"FTL Version: {pihole.ftl_current} (Latest: {pihole.ftl_latest}, Update Available: {pihole.ftl_update})"
            )

            print("\n=== Basic Statistics ===")
            print(f"Status: {pihole.status}")
            print(f"Domains being blocked: {pihole.domains_being_blocked}")
            print(f"Total queries today: {pihole.dns_queries_today}")
            print(f"Queries blocked today: {pihole.ads_blocked_today}")
            print(f"Percentage blocked: {pihole.ads_percentage_today}%")

            print("\n=== Client Statistics ===")
            print(f"Total clients ever seen: {pihole.clients_ever_seen}")
            print(f"Active clients: {pihole.unique_clients}")

            print("\n=== Query Statistics ===")
            print(f"Queries forwarded: {pihole.queries_forwarded}")
            print(f"Queries cached: {pihole.queries_cached}")
            print(f"Unique domains: {pihole.unique_domains}")

            print("\n=== Top Permitted Domains ===")
            for domain in pihole.top_queries:
                print(f"{domain['domain']}: {domain['count']} queries")

            print("\n=== Top Blocked Domains (Ads) ===")
            for domain in pihole.top_ads:
                print(f"{domain['domain']}: {domain['count']} queries")

            print("\n=== Forward Destinations ===")
            for upstream in pihole.forward_destinations:
                print(
                    f"Name: {upstream['name']}, IP: {upstream['ip']}, Count: {upstream['count']}"
                )

            print("\n=== Reply Types ===")
            for reply_type, count in pihole.reply_types.items():
                print(f"{reply_type}: {count}")

            print("\n=== Raw Data ===")
            print(
                json.dumps(
                    {
                        "data": pihole.data,
                        "blocked_domains": pihole.blocked_domains,
                        "permitted_domains": pihole.permitted_domains,
                        "clients": pihole.clients,
                        "upstreams": pihole.upstreams,
                        "blocking_status": pihole.blocking_status,
                        "versions": pihole.versions,
                    },
                    indent=4,
                    sort_keys=True,
                )
            )


async def toggle_blocking():
    """Example of enabling and disabling Pi-hole blocking."""
    async with aiohttp.ClientSession() as session:
        async with Hole(
            host=HOST,
            session=session,
            password=PASSWORD,
            protocol=PROTOCOL,
            port=PORT,
            verify_tls=VERIFY_TLS,
        ) as pihole:
            await pihole.get_data()
            initial_status = pihole.status
            print(f"\nInitial Pi-hole status: {initial_status}")

            print("\nDisabling Pi-hole blocking for 60 seconds...")
            disable_result = await pihole.disable(duration=60)

            await pihole.get_data()
            if pihole.status != "disabled":
                print(
                    f"ERROR: Failed to disable Pi-hole! Status is still: {pihole.status}"
                )
                return
            print(f"Successfully disabled Pi-hole. Status: {pihole.status}")
            print(f"Disable operation response: {disable_result}")

            print("\nWaiting 5 seconds...")
            await asyncio.sleep(5)

            print("\nEnabling Pi-hole blocking...")
            enable_result = await pihole.enable()

            await pihole.get_data()
            if pihole.status != "enabled":
                print(
                    f"ERROR: Failed to enable Pi-hole! Status is still: {pihole.status}"
                )
                return
            print(f"Successfully enabled Pi-hole. Status: {pihole.status}")
            print(f"Enable operation response: {enable_result}")

            if pihole.status == initial_status:
                print(
                    "\nToggle test completed successfully! Pi-hole returned to initial state."
                )
            else:
                print(
                    f"\nWARNING: Final status ({pihole.status}) differs from initial status ({initial_status})"
                )


if __name__ == "__main__":
    print(f"=== Pi-hole Statistics as of {datetime.now()} ===")
    asyncio.run(main())
    asyncio.run(toggle_blocking())
