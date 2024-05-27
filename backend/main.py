import uuid
import sanic
import routes
from database import db
from errors import custom_handler
from database.models.allocation import Allocation
from database.models.server import Server
from database.models.user import User
from database.models.banned_ips import BannedIPs
from database.dals.user_dal import UsersDAL
from core import session
from sanic_ext import Extend
from core.session import SessionManager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.caching import Cache
from core.general import populate_cache, load_config

app = sanic.Sanic("backend", env_prefix='APPLICATION_CONFIG_')
app.config.FALLBACK_ERROR_FORMAT = "auto"

app.config.CORS_ORIGINS = "http://127.0.0.1:5173"
app.config.CORS_SUPPORTS_CREDENTIALS = True
app.config.CORS_ALLOW_HEADERS = ["Content-Type", "Authorization"]
Extend(app) 


@app.before_server_start
async def main_start(app, loop):
    print("Loading yaml config file...")
    app.ctx.config = load_config("config.yml")
    print(f"Config with name {app.ctx.config['customization']['title']} loaded.")

    app.config.FALLBACK_ERROR_FORMAT = "json"

    await db.init(app.ctx.config["server"]["reset_on_reload"])
    print("Database initialized.")

    app.ctx.SESSION_EXPIRY_IN = app.ctx.config["session"]["session_max_age"]

    app.ctx.cache = Cache("cache.db")
    await app.ctx.cache.async__init__() 
    app.ctx.session = SessionManager("sessions.db")
    await app.ctx.session.async__init__()
    
    await populate_cache(app)

@app.after_server_start
async def ticker(app, loop):
    app.ctx.scheduler = AsyncIOScheduler()
    app.ctx.scheduler.add_job(app.ctx.session.session_cleanup, 'interval', seconds=app.ctx.config["session"]["session_cleanup_interval"])
    app.ctx.scheduler.start()

# Sanic exceptions - https://github.com/sanic-org/sanic/blob/main/sanic/exceptions.py

for index_version, api_routes in enumerate(routes.routes):
    print(f"Adding routes for version {index_version + 1}")
    for route in api_routes:
        print(f"Adding route {route[0]}")
        app.add_route(
            handler=route[1].as_view(),
            uri=f"/{route[0]}",
            version=index_version + 1, 
            version_prefix="/api/v"
        )

# disable access log