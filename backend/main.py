import sanic
from core.cors import setup_cors
import routes
from database import db
from errors import custom_handler
from database.models.allocation import Allocation
from database.models.server import Server
from database.models.user import User
from core import session
from sanic_ext import Extend
from core.session import SessionManager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.caching import Cache

app = sanic.Sanic("backend")
app.config.FALLBACK_ERROR_FORMAT = "auto"

app.config.CORS_ORIGINS = "http://127.0.0.1:5173"
app.config.CORS_SUPPORTS_CREDENTIALS = True
app.config.CORS_ALLOW_HEADERS = ["Content-Type", "Authorization"]
Extend(app)



@app.before_server_start
async def main_start(app, loop):
    #await db.init(True)
    print("Database initialized.")
    app.ctx.session = SessionManager("sessions.db")
    app.ctx.cache = Cache("cache.db")
    app.ctx.SESSION_EXPIRY_IN = 604800
    #app.error_handler = custom_handler.CustomErrorHandler()


@app.after_server_start
async def ticker(app, loop):
    app.ctx.scheduler = AsyncIOScheduler()
    app.ctx.scheduler.add_job(app.ctx.session.session_cleanup, 'interval', seconds=3600) # Runs session cleanup every hour
    app.ctx.scheduler.start()



# Sanic exceptions - https://github.com/sanic-org/sanic/blob/main/sanic/exceptions.py

for index_version, api_routes in enumerate(routes.routes):
    for route in api_routes:
        app.add_route(
            handler=route[1].as_view(),
            uri=f"/{route[0]}",
            version=index_version + 1, 
            version_prefix="/api/v"
        )

# disable access log