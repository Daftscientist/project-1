import sanic
import routes
from core import cache
from database import db
from errors import custom_handler

app = sanic.Sanic("backend")
app.config.FALLBACK_ERROR_FORMAT = "auto"
prefix = routes.routes_v1[0]

app.error_handler = custom_handler.CustomErrorHandler()

@app.on_event("startup")
async def startup():
    await db.init()
    await cache.init()

for route in routes.routes_v1[1]:
    app.add_route(
        handler=route[1],
        uri=f"/{prefix}{route[0]}",
    )
