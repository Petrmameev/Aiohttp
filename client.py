import asyncio

import aiohttp


async def main():
    async with aiohttp.ClientSession() as session:
        if not hasattr(session, "__aenter__"):
            print("Session object does not implement __aenter__ method")
        response = await session.post(
            "http://127.0.0.1:8080/user/",
            json={
                "name": "name_value",
                "description": "description_value",
                "owner": "owner_name",
            },
        )
        data = await response.text()
        print(data)
        response = await session.get(
            "http://127.0.0.1:8080/user/1/",
        )
        data = await response.text()
        print(data)

        response = await session.patch(
            "http://127.0.0.1:8080/user/1/", json={"name": "user_3"}
        )
        data = await response.json()
        print(data)

        response = await session.get(
            "http://127.0.0.1:8080/user/1/",
        )
        data = await response.json()
        print(data)

        response = await session.delete(
            "http://127.0.0.1:8080/user/1/",
        )
        data = await response.json()
        # print(data)

        response = await session.get(
            "http://127.0.0.1:8080/user/3/",
        )
        data = await response.json()
        print(data)


asyncio.run(main())
