import datetime
import re
import time
from sanic import Sanic
from sanic_dantic import parse_params, BaseModel
from core.responses import success
from sanic import Request, BadRequest
from sanic.views import HTTPMethodView
from core.cookies import check_if_cookie_is_present, send_cookie, get_session_id
import secrets
from database import db
from database.dals.user_dal import UsersDAL
from core.encoder import check_password


def create_session_id():
    """
    Creates a cryptographically-secure, URL-safe string
    """
    return secrets.token_urlsafe(16)  

EMAIL_REGEX = re.compile(r"^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$")

class LoginView(HTTPMethodView):
    """The login view."""

    class LoginRequest(BaseModel):
        """The create user request model."""

        email: str
        password: str
        two_factor_authentication_otp_code: str = None

    @parse_params(body=LoginRequest)
    async def post(self, request: Request, params: LoginRequest):
        """ The login route. """

        last_login = datetime.datetime.now()
        app = Sanic.get_app()
        ## check if cookies are present
        if await check_if_cookie_is_present(request):
            raise BadRequest("You are already logged in.")

        
        ## data validation - is it a real email
        if not EMAIL_REGEX.fullmatch(params.email):
            raise BadRequest("Email must be a valid email address.")
        
        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)

                if not await users_dal.check_if_user_exists_email(params.email):
                    raise BadRequest("Account does not exist.")

                user_info = await users_dal.get_user_by_email(params.email)
                if not await check_password(params.password.encode('utf-8'), user_info.password):
                    raise BadRequest("Password is incorrect.")

                if user_info.max_sessions <= len(await app.ctx.session.cocurrent_sessions(user_info.uuid)):
                    raise BadRequest("You have too many concurrent sessions.")

                uuid = user_info.uuid
                
                session_id = create_session_id()

                user_ip = request.remote_addr or request.ip

                if request.app.ctx.config["2fa"]["enabled"]: ## 2fa :)
                    if user_info.two_factor_authentication_enabled:
                        if len(params.two_factor_authentication_otp_code) is not request.app.ctx.config["2fa"]["digits"]:
                            raise BadRequest("Invalid OTP code.")
                        if not user_info.verify_two_factor_auth(params.two_factor_authentication_otp_code):
                            raise BadRequest("Invalid OTP code.")

                await app.ctx.session.add(session_id, uuid, user_ip, time.time() + app.ctx.SESSION_EXPIRY_IN)
                if not len(await app.ctx.session.cocurrent_sessions(user_info.uuid)) > 1:
                    await app.ctx.cache.update(user_info)
                await users_dal.update_user(uuid=uuid, last_login=last_login, latest_ip=user_ip)
                
                return send_cookie(request, "Logged in successfully.", {"session_id": session_id})