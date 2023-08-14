import re
from core.responses import Success
from database.dals.user_dal import UsersDAL
from sanic.views import HTTPMethodView
from sanic import Request, BadRequest
from core.cookies import get_user
from core.authentication import protected
from sanic_dantic import parse_params, BaseModel
from database import db
from core.session import edit_user

EMAIL_REGEX = re.compile(r"^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$")

class UpdateEmailView(HTTPMethodView):
    """The update email view."""

    class UpdateEmailRequest(BaseModel):
        """The update email request model."""

        current_email: str
        new_email: str
        repeated_new_email: str

    @staticmethod
    @protected
    @parse_params(body=UpdateEmailRequest)
    async def post(request: Request, params: UpdateEmailRequest):
        """The update email route."""
        user = await get_user(request)

        ## check validity of email
        if not EMAIL_REGEX.fullmatch(params.current_email):
            raise BadRequest("Email must be a valid email address.")
        if not EMAIL_REGEX.fullmatch(params.new_email):
            raise BadRequest("Email must be a valid email address.")
        if not EMAIL_REGEX.fullmatch(params.repeated_new_email):
            raise BadRequest("Email must be a valid email address.")
        
        ## check if email is already in use
        if not user["email"] == params.current_email:
            raise BadRequest("Current email is incorrect.")
        
        if params.new_email != params.repeated_new_email:
            raise BadRequest("New emails do not match.")
        
        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)
                if await users_dal.check_if_user_exists_email(params.new_email):
                    raise BadRequest("Email is taken.")
                
                await users_dal.update_user(user["uuid"], email=params.new_email)

                edit_user(user["session_id"], email=params.new_email)

        return await Success(request, "Email updated successfully.")