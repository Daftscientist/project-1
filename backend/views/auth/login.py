import datetime
import re
from sanic_dantic import parse_params, BaseModel
from core.responses import Success
from sanic import Request, BadRequest
from sanic.views import HTTPMethodView
from core.cookies import check_if_cookie_is_present, send_cookie
import secrets
from database import db
from database.dals.user_dal import UsersDAL
from core.encoder import check_password
from core.session import edit_user, get_user, add_user


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

    @parse_params(body=LoginRequest)
    async def post(self, request: Request, params: LoginRequest):
        """ The login route. """

        last_login = datetime.datetime.now()

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
                
                uuid = user_info.uuid
                
                session_id = create_session_id()

                max_sessions = user_info.max_sessions

                user_ip = request.remote_addr or request.ip

                res = add_user(max_sessions, last_login, user_ip, user_info.signup_ip, session_id, user_info.uuid, user_info.email, user_info.username, user_info.avatar, user_info.google_account_identifier, user_info.discord_account_identifier, user_info.created_at)
                
                if res == None:
                    raise BadRequest("You have too many sessions open. Please log out of one of your other sessions and try again.")

                users_dal.update_user()

                return send_cookie(request, "Logged in successfully.", {"uuid": str(uuid), "email": params.email, "session_id": session_id})