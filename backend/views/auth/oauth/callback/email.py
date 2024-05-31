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

class EmailAuthenticationCallbackView(HTTPMethodView):
    """The email authentication callback view."""

    @staticmethod
    async def get(request: Request, identifier: str):
        """ The email authentication callback route. """

        last_login = datetime.datetime.now()

        if not request.app.ctx.config["oauth"]["email"]["enabled"]:
            raise BadRequest("Email authentication is not enabled on this server.")

        if await check_if_cookie_is_present(request):
            raise BadRequest("You are already logged in.")
        
        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)
                
                user_info = await users_dal.get_user_by_email_login_identifier(identifier)

                if not user_info:
                    raise BadRequest("Invalid email authentication code.")

                if user_info.max_sessions <= len(await request.app.ctx.session.cocurrent_sessions(user_info.uuid)):
                    raise BadRequest("You have too many concurrent sessions.")

                if user_info.login_email_code_expiration < time.time():
                    raise BadRequest("Email authentication code has expired.")

                uuid = user_info.uuid
                
                session_id = create_session_id()

                user_ip = request.remote_addr or request.ip

                await request.app.ctx.session.add(session_id, uuid, user_ip, time.time() + request.app.ctx.SESSION_EXPIRY_IN)
                if not len(await request.app.ctx.session.cocurrent_sessions(user_info.uuid)) > 1:
                    await request.app.ctx.cache.update(user_info)
                await users_dal.update_user(uuid=uuid, last_login=last_login, latest_ip=user_ip)
                
                request.app.ctx.cache.update(
                    await users_dal.get_user_by_uuid(uuid)
                )
                
                if user_info.two_factor_authentication_enabled is True & request.app.ctx.config["2fa"]["enabled"] is True:
                    await request.app.ctx.session.change_twofactor_auth_state(session_id, True)
                    return send_cookie(request, "Logged in successfully. Your access is limited until you confirm your 2fa code.", {"session_id": session_id})
                else:
                    return send_cookie(request, "Logged in successfully.", {"session_id": session_id})