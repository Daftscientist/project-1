from sanic import Request, text, BadRequest
import re
from database.dals.user_dal import UsersDAL
from sanic_dantic import parse_params, BaseModel
from database import db
from core import encoder
from core.responses import Success
from core.cookies import check_if_cookie_is_present
from core.cache import add, CACHED_DATA

EMAIL_REGEX = re.compile(r"^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$")

from core.responses import Success
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
            return await BadRequest(request, "You are already logged in.")

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
                if await users_dal.check_if_user_exists(params.username, params.email):
                    return await BadRequest(request, "Email or username already exists.")
                
                await users_dal.create_user(params.username, params.email, await encoder.hash_password(params.password.encode('utf-8')))

                user_info = await users_dal.get_user_by_email(params.email)

                await add(user_info.identifier, user_info.uuid, user_info.email, user_info.username, user_info.avatar, user_info.google_account_identifier, user_info.discord_account_identifier, user_info.created_at)
                print(CACHED_DATA)

        return await Success(request, "User created successfully.")