import sanic
import routes
from core import cache
from database import db
from errors import custom_handler
from database.models.allocation import Allocation
from database.models.server import Server
from database.models.user import User

app = sanic.Sanic("backend")
app.config.FALLBACK_ERROR_FORMAT = "auto"
prefix = routes.routes_v1[0]

@app.main_process_start
async def main_start(*_):
    print(">>>>>> main_start <<<<<<")
    await db.init(False)
    await cache.init()

app.error_handler = custom_handler.CustomErrorHandler()

for route in routes.routes_v1[1]:
    app.add_route(
        handler=route[1],
        uri=f"/{prefix}{route[0]}",
    )
