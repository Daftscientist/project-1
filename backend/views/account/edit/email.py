import re
from core.responses import success
from database.dals.user_dal import UsersDAL
from sanic.views import HTTPMethodView
from sanic import Request, BadRequest
from core.authentication import protected
from sanic_dantic import parse_params, BaseModel
from database import db
from core.general import inject_cached_user

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
    @inject_cached_user()
    @parse_params(body=UpdateEmailRequest)
    async def post(request: Request, user, params: UpdateEmailRequest):
        """The update email route."""
        cache = request.app.ctx.cache

        ## check validity of email
        if not EMAIL_REGEX.fullmatch(params.current_email):
            raise BadRequest("Email must be a valid email address.")
        if not EMAIL_REGEX.fullmatch(params.new_email):
            raise BadRequest("Email must be a valid email address.")
        if not EMAIL_REGEX.fullmatch(params.repeated_new_email):
            raise BadRequest("Email must be a valid email address.")
        
        ## check if email is already in use
        if not user.email == params.current_email:
            raise BadRequest("Current email is incorrect.")
        
        if params.new_email != params.repeated_new_email:
            raise BadRequest("New emails do not match.")
        
        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)
                if await users_dal.check_if_user_exists_email(params.new_email):
                    raise BadRequest("Email is taken.")
                
                await users_dal.update_user(user.uuid, email=params.new_email)

                await cache.update(
                    await users_dal.get_user_by_uuid(
                        user.uuid
                    )
                )

        return await success(request, "Email updated successfully.")