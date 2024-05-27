import os
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
from core.oauth.discord import make_session, generate_oauth_url, handle_callback, get_user_info, get_user_avatar, get_user_email, get_user_id

app = sanic.Sanic("backend", env_prefix='APPLICATION_CONFIG_')
app.config.FALLBACK_ERROR_FORMAT = "auto"

app.config.CORS_ORIGINS = "http://127.0.0.1:5173"
app.config.CORS_SUPPORTS_CREDENTIALS = True
app.config.CORS_ALLOW_HEADERS = ["Content-Type", "Authorization"]
Extend(app) 


@app.before_server_start
async def main_start(app, loop):
    """
    Function to initialize the server before it starts.

    Args:
        app: The Flask application object.
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

    app.ctx.discord.make_session = make_session
    app.ctx.discord.generate_oauth_url = generate_oauth_url
    app.ctx.discord.handle_callback = handle_callback
    app.ctx.discord.get_user_info = get_user_info
    app.ctx.discord.get_user_avatar = get_user_avatar
    app.ctx.discord.get_user_email = get_user_email
    app.ctx.discord.get_user_id = get_user_id



@app.after_server_start
async def ticker(app, loop):
    """
    Starts a scheduler to periodically clean up sessions.

    Parameters:
    - app: The Quart application object.
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

# disable access log