from core.responses import success
from database.dals.user_dal import UsersDAL
from sanic.views import HTTPMethodView
from sanic import Request, BadRequest
from core.authentication import protected
from sanic_dantic import parse_params, BaseModel
from database import db


class UpdateUsernameView(HTTPMethodView):
    """The update username view."""

    class UpdateUsernameRequest(BaseModel):
        """The update username request model."""

        new_username: str

    @staticmethod
    @protected
    @parse_params(body=UpdateUsernameRequest)
    async def post(request: Request, user, params: UpdateUsernameRequest):
        """The update username route."""
        cache = request.app.ctx.cache

        ## check validity of email
        if len(params.new_username) < 3:
            raise BadRequest("Username must be at least 3 characters long.")
        
        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)
                if await users_dal.check_if_user_exists_username(params.new_username):
                    raise BadRequest("Username is taken.")
                
                await users_dal.update_user(user.uuid, username=params.new_username)

                await cache.update(
                    await users_dal.get_user_by_uuid(
                        user.uuid
                    )
                )

        return await success(request, "Username updated successfully.")