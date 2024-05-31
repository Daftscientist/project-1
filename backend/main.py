import os
import uuid
import sanic
from sanic_cors import CORS
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
from core.oauth import discord as discord_oauth_handler

app = sanic.Sanic("backend", env_prefix='APPLICATION_CONFIG_')
app.config.FALLBACK_ERROR_FORMAT = "auto"

CORS(
    app, automatic_options=True, allow_headers="application/json", expose_headers="application/json",
    resources={
        r"/*": {
            "origins": [
                "http://localhost:5173/",
                "http://localhost:5173",
                "http://127.0.0.1:5173/",
                "http://127.0.0.1:5173",
                "127.0.0.1:5173",
                "localhost:5173",
            ]
        }
    },
    supports_credentials=True
)
Extend(app) 

@app.middleware('response')
async def set_cors(request, response):
    response.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:5173"
    response.headers["Access-Control-Allow-Headers"] = "application/json"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Credentials"] = "true"

@app.before_server_start
async def main_start(app, loop):
    """
    Function to initialize the server before it starts.

    Args:
        app: The sanic application object.
        loop: The event loop.

    Returns:
        None
    """
    print("Loading yaml config file...")
    app.ctx.config = load_config("config.yml")
    print(f"Config with name {app.ctx.config['customization']['title']} loaded.")

    app.config.FALLBACK_ERROR_FORMAT = "json"

    if app.ctx.config["database"]["create_tables"]:
        if os.path.exists("cache.db"):
            os.remove("cache.db")
        if os.path.exists("sessions.db"):
            os.remove("sessions.db")
    
    await db.init(app.ctx.config["database"]["create_tables"]) 
    print("Database initialized.")

    app.ctx.SESSION_EXPIRY_IN = app.ctx.config["session"]["session_max_age"]

    app.ctx.cache = Cache("cache.db")
    await app.ctx.cache.async__init__() 
    app.ctx.session = SessionManager("sessions.db")
    await app.ctx.session.async__init__()
    
    await populate_cache(app)

    app.ctx.discord = discord_oauth_handler



@app.after_server_start
async def ticker(app, loop):
    """
    Starts a scheduler to periodically clean up sessions.

    Parameters:
    - app: The Sanic application object.
    - loop: The event loop.

    Returns:
    None
    """
    app.ctx.scheduler = AsyncIOScheduler()
    app.ctx.scheduler.add_job(app.ctx.session.session_cleanup, 'interval', seconds=app.ctx.config["session"]["session_cleanup_interval"])
    app.ctx.scheduler.start()

# Sanic exceptions - https://github.com/sanic-org/sanic/blob/main/sanic/exceptions.py

for index_version, api_routes in enumerate(routes.routes):
    config = load_config("config.yml")
    if (index_version + 1) in config["routing"]["enabled_versions"]:
        for route in api_routes:
            app.add_route(
                handler=route[1].as_view(),
                uri=f"/{route[0]}",
                version=index_version + 1, 
                version_prefix=config["routing"]["context_path"] + "/v"
            )

# serve static files without overriding the predefined routes above
app.static("/", "./static")
## serve them


# disable access log
