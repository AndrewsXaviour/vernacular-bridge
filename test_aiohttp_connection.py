import asyncio
import aiohttp


async def main():
    print("Testing aiohttp DNS + HTTPS...")

    try:
        timeout = aiohttp.ClientTimeout(total=15)

        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:
            async with session.get(
                "https://generativelanguage.googleapis.com"
            ) as response:
                print("SUCCESS")
                print("Status:", response.status)
                print("URL:", response.url)

    except Exception as e:
        print("FAILED")
        print("Exception type:", type(e).__name__)
        print("Exception:", repr(e))


if __name__ == "__main__":
    asyncio.run(main())