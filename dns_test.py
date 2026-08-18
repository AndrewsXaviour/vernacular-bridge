import asyncio
import socket
import aiohttp

async def main():
    print("1. Testing standard socket DNS resolution...")
    try:
        addr_info = socket.getaddrinfo("generativelanguage.googleapis.com", 443)
        print(f"   Success! Found {len(addr_info)} addresses.")
        for info in addr_info[:3]:
            print(f"   - {info[4]}")
    except Exception as e:
        print(f"   Failed: {e}")

    print("\n2. Testing aiohttp connection...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://generativelanguage.googleapis.com") as resp:
                print(f"   Success! Status: {resp.status}")
    except Exception as e:
        print(f"   Failed: {type(e).__name__} - {e}")

    print("\n3. Testing aiohttp with forced IPv4...")
    try:
        conn = aiohttp.TCPConnector(family=socket.AF_INET)
        async with aiohttp.ClientSession(connector=conn) as session:
            async with session.get("https://generativelanguage.googleapis.com") as resp:
                print(f"   Success! Status: {resp.status}")
    except Exception as e:
        print(f"   Failed: {type(e).__name__} - {e}")

asyncio.run(main())
