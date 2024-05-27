from datetime import time
import datetime
import secrets
from sanic import Request, BadRequest, redirect
from sanic.views import HTTPMethodView
from database.dals.user_dal import UsersDAL
from database import db
from core.cookies import check_if_cookie_is_present, send_cookie
from core.authentication import protected

def create_session_id():
    """
    Creates a cryptographically-secure, URL-safe string
    """
    return secrets.token_urlsafe(16) 

class DiscordOauthCallbackView(HTTPMethodView):
    """The discord oauth callback view."""

    @staticmethod
    @protected
    async def get(request: Request):
        """ The discord oauth callback route. """

        last_login = datetime.datetime.now()

        if not request.app.ctx.config["oauth"]["discord"]["enabled"]:
            raise BadRequest("Discord OAuth is not enabled on this server.")

        if await check_if_cookie_is_present(request):
            raise BadRequest("You are already logged in.")
        
        token = request.app.ctx.discord.handle_callback(request)
        discord_user_info = request.app.ctx.discord.get_user_info(token)
        
        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)
                
                user_info = await users_dal.get_user_by_email(discord_user_info["email"])

                if discord_user_info["id"] != user_info.discord_account_identifier:
                    raise BadRequest("Account does not exist.")

                if user_info.max_sessions <= len(await request.app.ctx.session.cocurrent_sessions(user_info.uuid)):
                    raise BadRequest("You have too many concurrent sessions.")

                uuid = user_info.uuid
                
                session_id = create_session_id()

                user_ip = request.remote_addr or request.ip

                await request.app.ctx.session.add(session_id, uuid, user_ip, time.time() + request.app.ctx.SESSION_EXPIRY_IN)
                if not len(await request.app.ctx.session.cocurrent_sessions(user_info.uuid)) > 1:
                    await request.app.ctx.cache.update(user_info)
                await users_dal.update_user(uuid=uuid, last_login=last_login, latest_ip=user_ip)

                if not user_info.avatar:
                    await users_dal.update_user(uuid=uuid, avatar=request.app.ctx.discord.get_user_avatar(discord_user_info["id"]))
                
                return send_cookie(request, "Logged in successfully.", {"session_id": session_id})