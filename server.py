import json

from models import Base, Session, User, engine
from sqlalchemy.exc import IntegrityError

from aiohttp import web

app = web.Application()


def get_http_error(http_error_class, message):
    return http_error_class(
        text=json.dumps({"error": message}), content_type="application/json")


async def orm_cntx(app: web.Application):
    print("START")
    async with engine.begin() as con:
        await con.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    print("SHUT DOWN")


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session as session:
        request["session"] = session
        response = await handler(request)
        return response


app.cleanup_ctx.append(orm_cntx)
app.middlewares.append(session_middleware)


async def get_user(user_id: int, session: Session) -> User:
    user = await session.get(User, user_id)
    if user is None:
        raise get_http_error(web.HTTPNotFound, "user not found")
    return user


class UserView(web.View):
    @property
    def session(self) -> Session:
        return self.request["session"]

    @property
    def user_id(self) -> int:
        return int(self.request.match_info["user_id"])

    async def get(self):
        user = await get_user(self.user_id, self.session)
        return web.json_response(
            {
                "id": user.id,
                "name": user.name,
                "description": user.description,
                "creations_time": user.creation_time.isoformat(),
                "owner": user.owner,
            }
        )

    async def post(self):
        json_data = await self.request.json()
        user = User(**json_data)
        try:
            self.session.add(user)
            await self.session.commit()
        except IntegrityError as err:
            raise get_http_error(web.HTTPConflict, "user already exists")
        user = await get_user(user.id, self.session)
        return web.json_response({"id": user.id})

    async def patch(self):
        json_data = await self.request.json()
        user = await get_user(self.user_id, self.session)
        for key, value in json_data.items():
            setattr(user, key, value)
        try:
            self.session.add(user)
            await self.session.commit()
        except IntegrityError as err:
            raise get_http_error(web.HTTPConflict, "user already exists")
        return web.json_response({"id": user.id})

    async def delete(self):
        user = await get_user(self.user_id, self.session)
        await self.session.delete(user)
        await self.session.commit()
        return web.json_response({"status": "deleted"})

app.add_routes(
    [
        web.get("/user/{user_id:\d+}/", UserView),
        web.patch("/user/{user_id:\d+}/", UserView),
        web.delete("/user/{user_id:\d+}/", UserView),
        web.post("/user/", UserView),
    ]
)

if __name__ == "__main__":
    web.run_app(app)
