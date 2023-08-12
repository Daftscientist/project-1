import sanic
import routes
import asyncio
from core import cache
from database import db
from errors import custom_handler

app = sanic.Sanic("backend")
app.config.FALLBACK_ERROR_FORMAT = "auto"
prefix = routes.routes_v1[0]

asyncio.run(db.init(True))
asyncio.run(cache.init())


app.error_handler = custom_handler.CustomErrorHandler()

for route in routes.routes_v1[1]:
    app.add_route(
        handler=route[1],
        uri=f"/{prefix}{route[0]}",
    )
