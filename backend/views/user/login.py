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

                add_user(session_id, user_info.uuid, user_info.email, user_info.username, user_info.avatar, user_info.google_account_identifier, user_info.discord_account_identifier, user_info.created_at)
                
                return send_cookie(request, "Logged in successfully.", {"uuid": str(uuid), "email": params.email, "session_id": session_id})



"""   @parse_params(body=LoginRequest)
    async def post(self, request: Request, params: LoginRequest):

        ## check if cookies are present
        if await check_if_cookie_is_present(request):
            raise BadRequest("You are already logged in.")

        ## data validation - is it a real email
        if not EMAIL_REGEX.fullmatch(params.email):
            raise BadRequest("Email must be a valid email address.")
        print(2)
        ## check if the user exists
        async with db.async_session() as session:
            async with session.begin():
                print(3)
                users_dal = UsersDAL(session)
                if not await users_dal.check_if_user_exists_email(params.email):
                    print(100)
                    raise BadRequest("Email does not exist.")
                print(4)
                ## check if the password is correct
                user_info = await users_dal.get_user_by_email(params.email)
                print(5)
                if not await check_password(params.password.encode('utf-8'), user_info.password):
                    print(200)
                    raise BadRequest("Password is incorrect.")
                print(6)
        print(CACHED_EMAIL_TO_UUID, "hello")
        uuid = await get_uuid(params.email)
        print(uuid)
        print(7)
        await update(uuid=uuid, session_id=await create_session_id())
        print(8)
        response = await Success(request, "Logged in successfully.")
        session_id = get(uuid=uuid)
        print(9)
        await set_cookie(response, {"uuid": uuid, "email": params.email, "session_id": session_id["session_id"]})
        print(10)
        print(CACHED_DATA, CACHED_DATA[uuid]["session_id"])
        return response"""