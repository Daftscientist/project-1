from datetime import datetime, timedelta
import re
import uuid
from sanic import Request, BadRequest, redirect
from sanic.views import HTTPMethodView
from core.responses import success
from database.dals.user_dal import UsersDAL
from core.cookies import check_if_cookie_is_present
from sanic_dantic import parse_params, BaseModel
from core.general import send_login_email

EMAIL_REGEX = re.compile(r"^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$")

class EmailAuthenticationView(HTTPMethodView):
    """The discord oauth view."""

    class EmailLoginRequest(BaseModel):
        """The email login request model."""
        email: str

    @staticmethod
    @parse_params(body=EmailLoginRequest)
    async def post(request: Request, params: EmailLoginRequest):
        """ The email authentication route. """

        if not request.app.ctx.config["oauth"]["email"]["enabled"]:
            raise BadRequest("Email authentication is not enabled on this server.")

        if not EMAIL_REGEX.fullmatch(params.email):
            raise BadRequest("Email must be a valid email address.")

        if await check_if_cookie_is_present(request):
            raise BadRequest("You are already logged in.")
        
        async with request.app.ctx.db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)
                user = await users_dal.get_user_by_email(params.email)
                if not user:
                    return success(request, "Login email successfully sent.")
                    ## This is here for security reasons, so that attackers cannot check if an email is registered or not.
                    ## The email is not registered, but we still send a success message to the user.

                if (user.login_email_code != None) and (user.login_email_code_expiration > datetime.now()):
                    raise BadRequest("Login email already sent. Please check your email.")

                if (user.login_email_code != None) and (user.login_email_code_expiration < datetime.now()):
                    await users_dal.update_user(
                        uuid=user.uuid,
                        login_email_code=None,
                        login_email_code_expiration=None
                    )
                
                UsersDAL.update_user(
                    uuid=user.uuid,
                    login_email_code=uuid.uuid4(),
                    login_email_code_expiration=datetime.now() + timedelta(seconds=request.app.ctx.config["oauth"]["email"]["expiry"])
                )

                cache = request.app.ctx.cache
                await cache.update(await users_dal.get_user_by_email(params.email))

                await send_login_email(request, cache.get(user.uuid))

                return success(request, "Login email successfully sent.")