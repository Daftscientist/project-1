from datetime import datetime
from sanic.views import HTTPMethodView
from sanic import BadRequest, Request
from core.cookies import check_if_cookie_is_present
from core.responses import success
from database.dals.user_dal import UsersDAL
from database import db
from sanic_dantic import parse_params, BaseModel
from core import encoder

class ResetPasswordCallbackView(HTTPMethodView):
    """The reset password view."""

    class ResetPasswordCallbackRequest(BaseModel):
        """The create user request model."""
        new_password: str
        repeated_new_password: str

    @staticmethod
    @parse_params(body=ResetPasswordCallbackRequest)
    async def post(request: Request, params: ResetPasswordCallbackRequest, identifier: str):
        """The password reset callback route."""
        
        if await check_if_cookie_is_present(request):
            raise BadRequest("You are already logged in.")
        
        if not (params.new_password == params.repeated_new_password):
            raise BadRequest("Both new password fields must be the same.")
        
        if len(params.new_password) < request.app.config["core"]["password_min_length"]:
            min_length = request.app.config["core"]["password_min_length"]
            raise BadRequest(f"Password must be at least {min_length} characters long.")

        if not identifier:
            raise BadRequest("No password reset code present in the request.", status_code=400)
        
        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)
                user = await users_dal.get_user_by_password_reset_code(identifier)
                if not user:
                    raise BadRequest("Invalid password reset code.", status_code=400)
                
                if user.password_reset_code_expiration < datetime.now():
                    raise BadRequest("Password reset code has expired.", status_code=400)

                await users_dal.update_user(
                    uuid=user.uuid,
                    password_reset_code=None,
                    password_reset_code_expiration=None,
                    password=await encoder.hash_password(params.new_password.encode('utf-8'))
                )

                return await success(request, "Password reset code is valid, password updated successfully.")
