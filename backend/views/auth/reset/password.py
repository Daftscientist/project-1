import re
import uuid
from sanic.views import HTTPMethodView
from sanic import BadRequest, Request
from core.cookies import check_if_cookie_is_present
from core.responses import success
from database.dals.user_dal import UsersDAL
from database import db
from sanic_dantic import parse_params, BaseModel
from core.general import send_password_reset_email

EMAIL_REGEX = re.compile(r"^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$")

class ResetPasswordView(HTTPMethodView):
    """The reset password view."""

    class ResetPasswordRequest(BaseModel):
        """The create user request model."""
        email: str

    @staticmethod
    @parse_params(body=ResetPasswordRequest)
    async def post(request: Request, params: ResetPasswordRequest):
        """The password reset route."""
        
        if await check_if_cookie_is_present(request):
            raise BadRequest("You are already logged in.")

        if not EMAIL_REGEX.fullmatch(params.email):
            raise BadRequest("Email must be a valid email address.")

        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)
                user = await users_dal.get_user_by_email(params.email)
                if not user:
                    raise BadRequest("Account does not exist.")
                
                users_dal.update_user(uuid=user.uuid, password_reset_code=uuid.uuid4())

                ## send the email
                send_password_reset_email(request, user)

                return await success(request, "Password reset code sent.")
                