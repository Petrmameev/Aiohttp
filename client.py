import asyncio

import aiohttp


async def main():
    async with aiohttp.ClientSession() as session:
        response = await session.post(
            "http://127.0.0.1:8000/user/",
            json={
                "name": "name_value",
                "description": "description_value",
                "owner": "owner_name",
            },
        )
        data = await response.json()
        print(data)




asyncio.run(main())
