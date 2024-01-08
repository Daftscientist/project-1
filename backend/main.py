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

app = sanic.Sanic("backend")
app.config.FALLBACK_ERROR_FORMAT = "auto"
prefix = routes.routes_v1[0]

app.config.CORS_ORIGINS = "http://127.0.0.1:5173"
app.config.CORS_SUPPORTS_CREDENTIALS = True
app.config.CORS_ALLOW_HEADERS = ["Content-Type", "Authorization"]
Extend(app)


@app.main_process_start
async def main_start(*_):
    await db.init(False)
    app.ctx.session = SessionManager("sessions.db")
    app.add_task(app.ctx.session.session_cleanup())
    app.ctx.SESSION_EXPIRY_IN = 604800

@app.after_server_start
async def ticker(app, loop):
    app.ctx.scheduler = AsyncIOScheduler()
    app.ctx.scheduler.add_job(app.ctx.session.session_cleanup(), 'interval', seconds=3600) # Runs session cleanup every hour
    app.ctx.scheduler.start()

app.error_handler = custom_handler.CustomErrorHandler()

# Sanic exceptions - https://github.com/sanic-org/sanic/blob/main/sanic/exceptions.py

for route in routes.routes_v1[1]:
    app.add_route(
        handler=route[1],
        uri=f"/{prefix}{route[0]}",
    )

# disable access log