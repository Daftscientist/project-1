import re
from sanic_dantic import parse_params, BaseModel
from core.responses import Success
from sanic import Request, BadRequest
from sanic.views import HTTPMethodView
from core.cookies import check_if_cookie_is_present, set_cookie
import secrets
from database import db
from database.dals.user_dal import UsersDAL
from core.encoder import check_password
from core.cache import get, update, get_uuid, CACHED_DATA

async def create_session_id():
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

        print(CACHED_DATA)

        ## check if cookies are present
        if await check_if_cookie_is_present(request):
            return await BadRequest(request, "You are already logged in.")
        
        ## data validation - is it a real email
        if not EMAIL_REGEX.fullmatch(params.email):
            return await BadRequest("Email must be a valid email address.")
        
        ## check if the user exists
        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)
                if not await users_dal.check_if_user_exists_email(params.email):
                    return await BadRequest(request, "Email does not exist.")
                
                ## check if the password is correct
                user_info = await users_dal.get_user_by_email(params.email)
                if not await check_password(params.password.encode('utf-8'), user_info.password):
                    return await BadRequest(request, "Password is incorrect.")

        uuid = await get_uuid(params.email)
        await update(uuid=uuid, session_id=await create_session_id())
        response = await Success(request, "Logged in successfully.")
        session_id = await get(uuid=uuid)
        await set_cookie(response, {"uuid": "test", "email": "", "session_id": session_id["session_id"]})
        print(CACHED_DATA, CACHED_DATA[uuid]["session_id"])
        return response