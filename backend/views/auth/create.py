import uuid
from sanic import Request, BadRequest
import re
import sanic
from core.general import send_verification_email, send_welcome_email
from database.dals.user_dal import UsersDAL
from sanic_dantic import parse_params, BaseModel
from database import db
from core import encoder
from core.responses import success
from core.cookies import check_if_cookie_is_present

EMAIL_REGEX = re.compile(r"^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$")

from core.responses import success
from sanic import Request, BadRequest
from sanic.views import HTTPMethodView
from core.cookies import check_if_cookie_is_present, remove_cookie


class CreateView(HTTPMethodView):
    """The create view."""

    class CreateUserRequest(BaseModel):
        """The create user request model."""

        username: str
        email: str
        password: str
        repeated_password: str

    @parse_params(body=CreateUserRequest)
    async def post(self, request: Request, params: CreateUserRequest):
        """The create user route."""
        
        if await check_if_cookie_is_present(request):
            raise BadRequest("You are already logged in.")

        ## data validation
        if len(params.username) < 3:
            raise BadRequest("Username must be at least 3 characters long.")
        if len(params.password) < 8:
            raise BadRequest("Password must be at least 8 characters long.")
        if params.password != params.repeated_password:
            raise BadRequest("Passwords do not match.")
        if not EMAIL_REGEX.fullmatch(params.email):
            raise BadRequest("Email must be a valid email address.")

        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)
                if await users_dal.check_if_user_exists_email(params.email):
                    raise BadRequest("Email or username is taken.")

                if await users_dal.check_if_user_exists(params.username, params.email):
                    raise BadRequest("Email or username is taken.")
                
                ip = request.ip or request.remote_addr

                await users_dal.create_user(
                    params.username, 
                    params.email,
                    await encoder.hash_password(params.password.encode('utf-8')),
                    ip, ip
                )

                if not request.app.ctx.config["email"]["verification_email"]["enabled"]: ## fix to stay false
                    user = await users_dal.get_user_by_email(params.email)
                    await users_dal.update_user(email_verified=True, uuid=user.uuid, email_verification_code=None)
                
                if request.app.ctx.config["email"]["verification_email"]["enabled"]:
                    await send_verification_email(request)
                
                if request.app.ctx.config["email"]["welcome_email"]["enabled"]:
                    await send_welcome_email(request)

        return await success(request, "User created successfully.")